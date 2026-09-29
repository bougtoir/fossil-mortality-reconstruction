"""Make remaining manuscript figures: generative scheme, fossil demos,
sensitivity tornado."""
import numpy as np, pandas as pd, sys
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
sys.path.insert(0, '.')
from mortality_models import MortalityModel, observed_density
from fitting import fit_mle

# ----------------------------------------------------------- scheme figure
fig, ax = plt.subplots(figsize=(11, 3.6)); ax.axis('off')
boxes = [
    (0.00, 'Latent mortality\nμ(a), S(a), f(a)\nWeibull / Gompertz–Makeham\nSiler / piecewise'),
    (0.17, 'Assemblage\nattritional: f(a)\ncatastrophic: S(a)e^{−ra}'),
    (0.36, 'Observation\nq(a): preservation,\nrecovery, collection'),
    (0.55, 'Age estimation\nexact / interval /\nlower bound / error'),
    (0.74, 'Report types\nindividual ages\ngrouped / max-only'),
]
for x, txt in boxes:
    ax.add_patch(FancyBboxPatch((x, 0.25), 0.15, 0.55,
                 boxstyle='round,pad=0.02', fc='#eef3fb', ec='#3a5a8c'))
    ax.text(x + 0.075, 0.52, txt, ha='center', va='center', fontsize=8)
for i in range(4):
    ax.annotate('', xy=(0.17 + 0.19 * i, 0.52), xytext=(0.15 + 0.19 * i, 0.52),
                arrowprops=dict(arrowstyle='->', lw=1.5, color='#3a5a8c'))
ax.text(0.5, 0.05, 'g(a) ∝ base(a) · q(a)  →  likelihood terms: individuals, bins, order statistics',
        ha='center', fontsize=9, style='italic')
ax.set_xlim(-0.02, 1.0); ax.set_ylim(0, 1)
fig.tight_layout(); fig.savefig('../output/figures/fig_scheme.png', dpi=170); plt.close(fig)

# ----------------------------------------------------------- fossil demo fig
AGES = np.linspace(1e-4, 30, 3500)
df = pd.read_csv('../data/processed/maiasaura_woodward2015_tibiae.csv')
lag = pd.to_numeric(df['lag_count'], errors='coerce').dropna().values
st = [{'type': 'ages', 'intervals': [(a, a + 1.0) for a in lag]}]

fig, axs = plt.subplots(1, 3, figsize=(13.5, 4.2))
ax = axs[0]
ax.hist(lag, bins=np.arange(-0.25, 11.75, 0.5), color='#888', alpha=0.8)
ax.set_xlabel('LAG count (= age class, yr)'); ax.set_ylabel('specimens')
ax.set_title(f'Maiasaura tibiae (n={len(lag)}), Woodward et al. 2015')

ax = axs[1]
for fam, c in [('weibull', '#1f77b4'), ('gompertz_makeham', '#2ca02c'), ('siler', '#d62728')]:
    m, _ = fit_mle(fam, AGES, st, seed=1)
    ax.plot(AGES, m.S(AGES), color=c, label=fam.replace('_', '-'))
ax.step(np.append(np.sort(lag), 12), 1 - np.arange(1, len(lag) + 2) / (len(lag) + 1),
        'k--', where='post', lw=1.2, label='empirical 1−ECDF')
ax.set_xlabel('age (yr)'); ax.set_ylabel('S(a)'); ax.set_xlim(0, 15)
ax.set_title('Latent survival fits (attritional, q=1)'); ax.legend(fontsize=8)

ax = axs[2]
sens = pd.read_csv('../output/tables/phase7_sensitivity.csv')
sens = sens[~sens.fail]
base = sens[sens.analysis == 'baseline'].set_index('family')['median']
show = sens[sens.analysis.isin(['baseline', 'q_juvdef', 'q_logistic',
        'ageerr_plus1lag', 'exclude_age0', 'exclude_top10pct',
        'standing_r+0.00', 'standing_r-0.10', 'standing_r+0.10',
        'prior_sd1.5', 'prior_sd4.0'])]
labs = {'baseline': 'baseline', 'q_juvdef': 'q: juvenile deficit',
        'q_logistic': 'q: logistic detection', 'ageerr_plus1lag': 'age error +1 LAG',
        'exclude_age0': 'exclude age-0 specimens', 'exclude_top10pct': 'exclude oldest 10%',
        'standing_r+0.00': 'standing crop, r=0', 'standing_r-0.10': 'standing crop, r=−0.10',
        'standing_r+0.10': 'standing crop, r=+0.10', 'prior_sd1.5': 'prior sd=1.5',
        'prior_sd4.0': 'prior sd=4.0'}
fam_marks = {'weibull': 'o', 'gompertz_makeham': 's', 'siler': '^'}
ypos = {a: i for i, a in enumerate(show.analysis.unique())}
for _, r in show.iterrows():
    ax.scatter(r['median'], ypos[r['analysis']], marker=fam_marks.get(r['family'], 'x'),
               s=45, color='#3a5a8c')
ax.set_yticks(range(len(ypos)), [labs.get(a, a) for a in show.analysis.unique()], fontsize=8)
ax.invert_yaxis(); ax.set_xlabel('estimated median age at death (yr)')
ax.set_title('Sensitivity of Maiasaura median estimate\n(markers = model family)')
fig.tight_layout(); fig.savefig('../output/figures/fig_fossil_fits.png', dpi=170)
print('figures done')
