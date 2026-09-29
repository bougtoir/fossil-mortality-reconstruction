"""Phase 3 — identifiability demonstrations.

A) (F, q) non-identifiability: biased estimates under wrong q + a likelihood
   ridge along the iso-g manifold.
B) Catastrophic assemblage: r confounded with mortality parameters.
C) Maximum-only evidence: weak identification; role of n.
Outputs: output/figures/fig_identifiability.png, output/tables/identifiability_*.csv
"""
import numpy as np, sys, json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
sys.path.insert(0, '.')
from mortality_models import (MortalityModel, observed_density, _cdf_from_density,
                              expected_max, mortality_targets)
from fitting import fit_mle, study_loglik, build_negloglik

rng = np.random.default_rng(20260929)
ages = np.linspace(1e-4, 40, 4001)


def sample_g(g, ages, n, rng):
    G = _cdf_from_density(ages, g)
    u = rng.random(n)
    return np.interp(u, G, ages)


# ============================================================ DEMO A
truth = MortalityModel('weibull', [10.0, 2.0])
qkw_true = dict(q_adult=1.0, age_full=6.0)
g_true = observed_density(truth, ages, 'attritional', 0.0,
                          'juvenile_deficit', qkw_true)
n_obs = 50
obs = sample_g(g_true, ages, n_obs, rng)
studies = [{'type': 'ages', 'intervals': [(a, a) for a in obs]}]

scenarios = {
    'correct_q': ('juvenile_deficit', qkw_true),
    'constant_q': ('constant', {}),
    'saturating_q': ('saturating', dict(qmax=1.0, rate=0.5)),
}
rows = []
fits = {}
for name, (qf, qk) in scenarios.items():
    m, info = fit_mle('weibull', ages, studies, q_family=qf, q_kw=qk, seed=3)
    tg = mortality_targets(m, ages)
    rows.append(dict(scenario=name, lam=m.params[0], k=m.params[1],
                     median=tg['median'], mean=tg['mean_age'], q90=tg['q90'],
                     E_M50=tg['E_M50'], nll=info['nll']))
    fits[name] = (m, qf, qk)
tg_true = mortality_targets(truth, ages)
for r_ in rows: r_['true_median'] = tg_true['median']; r_['true_mean'] = tg_true['mean_age']

# iso-g manifold: optimize a constant-q alternative (lam,k) to reproduce the
# biased observed density as closely as possible.
from scipy.optimize import minimize as _min
def _dg(x):
    mm = MortalityModel('weibull', np.exp(x))
    gg = observed_density(mm, ages, 'attritional', 0.0, 'constant', {})
    return np.sum((gg - g_true) ** 2)
res_iso = _min(_dg, np.log([8.0, 2.0]), method='Nelder-Mead')
alt = MortalityModel('weibull', np.exp(res_iso.x))
g_alt = observed_density(alt, ages, 'attritional', 0.0, 'constant', {})
dmax = float(np.max(np.abs(g_true - g_alt)))
ll_true = study_loglik(g_true, ages, studies)
ll_alt = study_loglik(g_alt, ages, studies)

# likelihood surface over (lam,k) under the two q assumptions
lams = np.linspace(4, 20, 33); ks = np.linspace(0.8, 4.0, 33)
LL_a = np.zeros((lams.size, ks.size)); LL_b = np.zeros_like(LL_a)
for i, la in enumerate(lams):
    for j, k in enumerate(ks):
        mm = MortalityModel('weibull', [la, k])
        LL_a[j, i] = study_loglik(observed_density(mm, ages, 'attritional', 0.0, 'juvenile_deficit', qkw_true), ages, studies)
        LL_b[j, i] = study_loglik(observed_density(mm, ages, 'attritional', 0.0, 'constant', {}), ages, studies)

# ============================================================ DEMO B
truth_b = MortalityModel('siler', [0.4, 1.0, 0.05, 0.005, 0.25])
r_true = -0.05
g_cat = observed_density(truth_b, ages, 'catastrophic', r_true, 'constant', {})
obs_b = sample_g(g_cat, ages, 80, rng)
studies_b = [{'type': 'ages', 'intervals': [(a, a) for a in obs_b]}]

# profile likelihood over assumed r for a Weibull fit
rs = np.linspace(-0.20, 0.20, 29)
prof = []
for r in rs:
    m, info = fit_mle('weibull', ages, studies_b, assemblage='catastrophic',
                      r=r, seed=5, n_starts=3)
    if m is None:
        prof.append(dict(r=r, nll=np.nan, lam=np.nan, k=np.nan, median=np.nan, mean=np.nan))
    else:
        tg = mortality_targets(m, ages)
        prof.append(dict(r=r, nll=info['nll'], lam=m.params[0], k=m.params[1],
                         median=tg['median'], mean=tg['mean_age']))
prof = [p for p in prof if np.isfinite(p['nll'])]
nlls = np.array([p['nll'] for p in prof])
span = nlls.max() - nlls.min()
i_best = int(np.argmin(nlls))

# ============================================================ DEMO C
truth_c = MortalityModel('weibull', [10.0, 2.0])
g_c = observed_density(truth_c, ages, 'attritional', 0.0, 'constant', {})
# same latent truth; two reports: M5 and M100 drawn honestly
def max_report(n_rep, n_draws):
    reps = [np.max(sample_g(g_c, ages, n_draws, rng)) for _ in range(n_rep)]
    return reps
m5 = max_report(3, 5); m100 = max_report(3, 100)
E_M5, E_M100 = expected_max(g_c, ages, 5), expected_max(g_c, ages, 100)

# profile likelihood surfaces over (lam,k) for each single max-only report
def maxonly_surface(m, n):
    LL = np.zeros((lams.size, ks.size))
    st = [{'type': 'max_only', 'm': m, 'n': n}]
    for i, la in enumerate(lams):
        for j, k in enumerate(ks):
            mm = MortalityModel('weibull', [la, k])
            gg = observed_density(mm, ages, 'attritional', 0.0, 'constant', {})
            LL[j, i] = study_loglik(gg, ages, st)
    return LL
LL_m5 = maxonly_surface(m5[0], 5)
LL_m100 = maxonly_surface(m100[0], 100)

# ============================================================ FIGURE
fig, axs = plt.subplots(1, 3, figsize=(13.5, 4.2))

ax = axs[0]
cs = ax.contourf(lams, ks, LL_b - LL_b.max(), levels=np.linspace(-10, 0, 21), cmap='viridis')
ax.plot(tg_true['mean_age'] * 0 + 10.0, 2.0, 'r*', ms=14, label='truth')
ax.set_xlabel('Weibull scale λ'); ax.set_ylabel('Weibull shape k')
ax.set_title('A  q misspecified (assumed constant)\nlive juvenile under-recovery truth')
plt.colorbar(cs, ax=ax, label='loglik − max')

ax = axs[1]
rr = np.array([p['r'] for p in prof]); mm = np.array([p['mean'] for p in prof])
ax.plot(rr, mm, 'o-')
ax.axvline(r_true, color='r', ls='--', label=f'true r={r_true}')
ax.set_xlabel('assumed growth rate r'); ax.set_ylabel('est. mean age at death (yr)')
ax.set_title('B  catastrophic assemblage\nlifespan estimate vs assumed r')
ax.legend()

ax = axs[2]
cs = ax.contourf(lams, ks, LL_m5 - LL_m5.max(), levels=np.linspace(-10, 0, 21), cmap='viridis')
ax.plot(10.0, 2.0, 'r*', ms=14)
ax.set_xlabel('Weibull scale λ'); ax.set_ylabel('Weibull shape k')
ax.set_title(f'C  max-only report M_5={m5[0]:.1f} yr\n(n=5 behind the maximum)')
plt.colorbar(cs, ax=ax, label='loglik − max')
fig.tight_layout()
fig.savefig('../output/figures/fig_identifiability.png', dpi=160)

# ============================================================ write tables
import pandas as pd
pd.DataFrame(rows).to_csv('../output/tables/identifiability_q_scenarios.csv', index=False)
pd.DataFrame(prof).to_csv('../output/tables/identifiability_r_profile.csv', index=False)
with open('../output/tables/identifiability_summary.json', 'w') as f:
    json.dump(dict(
        iso_g_max_density_diff=dmax, loglik_true_pair=ll_true, loglik_alt_pair=ll_alt,
        r_profile_nll_span=float(span), r_best=float(rr[i_best]),
        E_M5=E_M5, E_M100=E_M100,
        max5_reports=[float(x) for x in m5], max100_reports=[float(x) for x in m100],
        obs_sample=obs.tolist(), obs_cat=obs_b.tolist()), f, indent=1)
print('A: scenario fits')
print(pd.DataFrame(rows).round(3).to_string())
print('iso-g max |dg| =', round(dmax, 6), ' ll(true)=', round(ll_true, 1), ' ll(alt)=', round(ll_alt, 1))
print('B: r profile nll span =', round(span, 2), 'best r =', round(float(rr[i_best]), 3))
print('C: E[M5] =', round(E_M5, 1), ' E[M100] =', round(E_M100, 1), ' reports:', np.round(m5, 1), np.round(m100, 1))
