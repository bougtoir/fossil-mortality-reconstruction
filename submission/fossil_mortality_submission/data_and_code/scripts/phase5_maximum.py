"""Phase 5 — maximum observed age as evidence.

(a) Model comparison: A individual ages only / B max-only / C combined
    independent / D double-counted (the max from the SAME dataset, wrongly
    added as independent likelihood) — simulation only.
(b) M_5 vs M_100 are not comparable statistics; standardized E[M_n*] proposal.
Outputs: output/tables/phase5_*.csv, output/figures/fig_maximum.png
"""
import numpy as np, pandas as pd, sys, json
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
sys.path.insert(0, '.')
from mortality_models import MortalityModel, observed_density, expected_max, _cdf_from_density
from fitting import fit_mle
from scipy.optimize import minimize

rng = np.random.default_rng(777)
ages = np.linspace(1e-4, 60, 6001)


def sample_g(g, n, rng):
    G = _cdf_from_density(ages, g)
    return np.interp(rng.random(n), G, ages)


truth = MortalityModel('weibull', [10.0, 2.0])
g_true = observed_density(truth, ages)
REPS = 60
rows = []
for rep in range(REPS):
    obs = sample_g(g_true, 40, rng)
    m = float(obs.max())
    st_ind = [{'type': 'ages', 'intervals': [(a, a) for a in obs]}]
    st_max = [{'type': 'max_only', 'm': m, 'n': 40}]
    st_comb = st_ind + [{'type': 'max_only', 'm': m, 'n': 40,
                         'external': False}]
    # Model C: individuals + the dataset max as a max_only term — this IS
    # the double-counting error when the max came from the same data.
    # A legitimate combined term would use an INDEPENDENT max report:
    m_ext = float(sample_g(g_true, 30, rng).max())
    st_comb_ok = st_ind + [{'type': 'max_only', 'm': m_ext, 'n': 30}]
    st_dbl = st_ind + [dict(type='max_only', m=m, n=40)]
    for label, st in [('A_individual', st_ind), ('B_maxonly', st_max),
                      ('C_combined_indep', st_comb_ok), ('D_doublecounted', st_dbl)]:
        mo, info = fit_mle('weibull', ages, st, seed=rep, n_starts=4)
        if mo is None:
            continue
        lam, k = mo.params
        rows.append(dict(rep=rep, model=label, lam=lam, k=k,
                         median=float(ages[np.argmin(np.abs(
                             _cdf_from_density(ages, mo.f(ages)) - 0.5))]),
                         E_M50=expected_max(mo.f(ages), ages, 50)))
df = pd.DataFrame(rows)
df.to_csv('../output/tables/phase5_model_comparison.csv', index=False)
summ = df.groupby('model')[['lam', 'median', 'E_M50']].agg(
    ['mean', 'std', lambda x: np.percentile(x, 5), lambda x: np.percentile(x, 95)])
print(summ.round(2).to_string())

# (b) M_n comparability: distribution of M_5 vs M_100 from same truth
for nn in [5, 40, 100]:
    mmax = expected_max(g_true, ages, nn)
    print(f'E[M_{nn}] = {mmax:.1f}')
# observed max under a juvenile-deficit q (what museums actually record)
g_obs = observed_density(truth, ages, 'attritional', 0.0,
                         'juvenile_deficit', dict(q_adult=1.0, age_full=6.0))
for nn in [5, 40, 100]:
    print(f'observed-process E[M_{nn}] = {expected_max(g_obs, ages, nn):.1f}')

fig, axs = plt.subplots(1, 2, figsize=(10, 4))
ax = axs[0]
for lab, grp in df.groupby('model'):
    ax.hist(grp['median'], bins=20, alpha=0.5, label=lab, density=True)
ax.axvline(8.33, color='k', ls='--', label='truth')
ax.set_xlabel('estimated median age at death (yr)'); ax.legend(fontsize=8)
ax.set_title('Median estimate by evidence model')
ax = axs[1]
ns = np.arange(1, 201)
ax.plot(ns, [expected_max(g_true, ages, n) for n in ns], label='latent f')
ax.plot(ns, [expected_max(g_obs, ages, n) for n in ns], '--', label='observed g (juv. deficit)')
ax.set_xlabel('sample size n'); ax.set_ylabel('E[M_n] (yr)')
ax.set_title('The "oldest individual" is a sample-size statistic')
ax.legend(); fig.tight_layout()
fig.savefig('../output/figures/fig_maximum.png', dpi=160)
json.dump({'E_M5': expected_max(g_true, ages, 5),
           'E_M40': expected_max(g_true, ages, 40),
           'E_M100': expected_max(g_true, ages, 100),
           'obs_E_M40': expected_max(g_obs, ages, 40),
           'obs_E_M100': expected_max(g_obs, ages, 100)},
          open('../output/tables/phase5_expected_maxima.json', 'w'), indent=1)
