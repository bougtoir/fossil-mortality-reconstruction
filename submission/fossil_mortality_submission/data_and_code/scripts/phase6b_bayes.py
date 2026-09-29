"""Phase 6b — Bayesian demonstration on the Maiasaura tibia assemblage.

emcee posterior for Weibull + Siler under the primary scenario
(attritional + constant q). Posterior predictive check: the dataset's
observed maximum (10 LAGs) compared against predicted M_49 distribution.
Outputs: output/tables/phase6b_posterior.csv, output/figures/fig_posterior.png
"""
import numpy as np, pandas as pd, sys, json
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
sys.path.insert(0, '.')
from mortality_models import (MortalityModel, observed_density,
                              _cdf_from_density, mortality_targets)
from fitting import sample_posterior, make_model

AGES = np.linspace(1e-4, 30, 3500)
df = pd.read_csv('../data/processed/maiasaura_woodward2015_tibiae.csv')
lag = pd.to_numeric(df['lag_count'], errors='coerce').dropna().values
n = len(lag); m_obs = float(lag.max())
st = [{'type': 'ages', 'intervals': [(a, a + 1.0) for a in lag]}]

res = {}
for fam in ['weibull', 'siler']:
    r = sample_posterior(fam, AGES, st, n_steps=5000, burn=2000, seed=4)
    res[fam] = r
    print(fam, 'acc', round(r['acc'], 2), 'chain', r['chain'].shape)

rows = []
fig, axs = plt.subplots(1, 3, figsize=(13, 4))
col = {'weibull': '#1f77b4', 'siler': '#d62728'}
for fam, r in res.items():
    S = np.zeros((r['chain'].shape[0], AGES.size)); M50 = np.zeros(r['chain'].shape[0])
    MED = np.zeros_like(M50); MEAN = np.zeros_like(M50)
    for i, x in enumerate(r['chain']):
        m = make_model(fam, x)
        tg = mortality_targets(m, AGES)
        S[i] = m.S(AGES); M50[i] = tg['E_M50']; MED[i] = tg['median']; MEAN[i] = tg['mean_age']
    lo, hi = np.percentile(S, [2.5, 97.5], axis=0)
    axs[0].fill_between(AGES, lo, hi, alpha=0.25, color=col[fam], label=fam)
    rows.append(dict(family=fam,
                     median_lo=np.percentile(MED, 2.5), median=np.median(MED),
                     median_hi=np.percentile(MED, 97.5),
                     mean_lo=np.percentile(MEAN, 2.5), mean=np.median(MEAN),
                     mean_hi=np.percentile(MEAN, 97.5),
                     EM50_lo=np.percentile(M50, 2.5), EM50=np.median(M50),
                     EM50_hi=np.percentile(M50, 97.5)))
    axs[1].hist(M50, bins=40, alpha=0.5, color=col[fam], label=fam, density=True)
    # posterior predictive p-value for the observed maximum
    m_med = make_model(fam, np.median(r['chain'], axis=0))
    g = observed_density(m_med, AGES)
    G = _cdf_from_density(AGES, g)
    rng = np.random.default_rng(0)
    sim_max = np.interp(rng.random((1500, n)), G, AGES).max(axis=1)
    p_max = float(np.mean(sim_max >= m_obs))
    rows[-1]['postpred_p_max'] = p_max
    rows[-1]['obs_max'] = m_obs

axs[0].plot(AGES, np.ones_like(AGES) * np.nan, ' ')
ecdf = np.sort(lag); axs[0].step(np.append(ecdf, 15), np.arange(1, n + 2) / (n + 1),
                                 'k-', where='post', label='empirical S (1-ECDF)')
axs[0].set_xlabel('age (yr)'); axs[0].set_ylabel('S(a)')
axs[0].set_title('Posterior survival bands vs empirical'); axs[0].legend()
axs[1].axvline(m_obs, color='k', ls='--', label=f'observed max = {m_obs:.0f}')
axs[1].set_xlabel('E[M_50] (yr)'); axs[1].set_title('Posterior of standardized max')
axs[1].legend()
ax = axs[2]
for fam, r in res.items():
    ax.hist(np.exp(r['chain'][:, -1]) if fam == 'siler' else np.exp(r['chain'][:, 1]),
            bins=40, alpha=0.5, color=col[fam], density=True,
            label=('Siler b3' if fam == 'siler' else 'Weibull k'))
ax.set_title('Shape parameter posteriors'); ax.legend()
fig.tight_layout(); fig.savefig('../output/figures/fig_posterior.png', dpi=170)

pd.DataFrame(rows).to_csv('../output/tables/phase6b_posterior.csv', index=False)
print(pd.DataFrame(rows).round(2).to_string())
