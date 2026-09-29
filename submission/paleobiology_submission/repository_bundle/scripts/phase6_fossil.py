"""Phase 6 — fossil proof-of-concept analyses.

Datasets (see data_inventory.csv):
  1. Maiasaura peeblesorum tibiae, Woodward et al. 2015 (n=50 LAG counts)
  2. Psittacosaurus lujiatunensis, Zhao et al. 2013 (n=16, mixed/unknown assemblage)
  3. Morganucodon + Kuehneotherium cementum annulations, Newham et al. 2020
     (n=35, 27; 3 observers → measurement uncertainty)
  4. Albertosaurus sarcophagus lx (per 1000) from Erickson via Griebeler 2021
     Dryad README (n=22 implied) — grouped likelihood.

Each dataset is fit under multiple model families, assemblage mechanisms and
q scenarios. Outputs: output/tables/phase6_*.csv, output/figures/fig_fossil_*.png
"""
import numpy as np, pandas as pd, sys, json
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
sys.path.insert(0, '.')
from mortality_models import (MortalityModel, observed_density, expected_max,
                              mortality_targets, _cdf_from_density)
from fitting import fit_mle
from scipy.stats import multinomial

FAMS = ['weibull', 'gompertz_makeham', 'siler']
Ages = np.linspace(1e-4, 45, 5000)


def fit_all(studies, assemblage, r, q_family, q_kw, ages=Ages, seed=0):
    out = {}
    for fam in FAMS:
        m, info = fit_mle(fam, ages, studies, assemblage=assemblage, r=r,
                          q_family=q_family, q_kw=q_kw, seed=seed, n_starts=5)
        if m is not None:
            tg = mortality_targets(m, ages)
            out[fam] = dict(model=m, info=info, targets=tg)
    return out


def summarize_fit(tag, fam, fit):
    tg = fit['targets']
    return dict(dataset=tag, family=fam,
                median=tg['median'], mean=tg['mean_age'], q90=tg['q90'],
                q95=tg['q95'], E_M50=tg['E_M50'], E_M100=tg['E_M100'],
                juv_haz=tg['juvenile_hazard'], prime_haz=tg['prime_hazard'],
                late_slope=tg['late_hazard_slope'], hazmin=tg['hazard_min_age'],
                nll=fit['info']['nll'], converged=fit['info']['converged'])


def postpred_counts(model, ages, edges, n, assemblage, r, qf, qkw, reps=2000, seed=1):
    g = observed_density(model, ages, assemblage, r, qf, qkw)
    G = _cdf_from_density(ages, g)
    rng = np.random.default_rng(seed)
    bi = np.searchsorted(edges, ages) - 1
    probs = np.zeros(len(edges) - 1)
    for i in range(len(probs)):
        probs[i] = np.trapezoid(g[(ages >= edges[i]) & (ages < edges[i + 1])],
                                ages[(ages >= edges[i]) & (ages < edges[i + 1])])
    probs = probs / probs.sum()
    return probs, multinomial.rvs(n, probs, size=reps, random_state=rng)


rows = []

# ============================================================ 1. Maiasaura
df = pd.read_csv('../data/processed/maiasaura_woodward2015_tibiae.csv')
lag = pd.to_numeric(df['lag_count'], errors='coerce').dropna().values
n_maia = len(lag)
max_maia = float(lag.max())
# LAG count x → age in [x, x+1); a possible eroded inner LAG handled in sensitivity
ivs = [(a, a + 1.0) for a in lag]
studies_maia = [{'type': 'ages', 'intervals': ivs}]

maia = {}
for (asm, r_, qf, qkw, tag) in [
        ('attritional', 0.0, 'constant', {}, 'attritional|q_const'),
        ('attritional', 0.0, 'juvenile_deficit', {'q_adult': 1.0, 'age_full': 3.0},
         'attritional|q_juvdef'),
        ('attritional', 0.0, 'juvenile_deficit_sq', {'q_adult': 1.0, 'age_full': 3.0},
         'attritional|q_juvdef_sq'),
        ('catastrophic', 0.0, 'constant', {}, 'standing|r0'),
        ('catastrophic', -0.05, 'constant', {}, 'standing|r-0.05'),
        ('catastrophic', 0.05, 'constant', {}, 'standing|r+0.05')]:
    res = fit_all(studies_maia, asm, r_, qf, qkw)
    for fam, fit in res.items():
        rows.append(summarize_fit(f'Maiasaura|{tag}', fam, fit))
    maia[tag] = res

# model comparison on primary scenario
prim = maia['attritional|q_const']
for fam, f in prim.items():
    pass
# posterior predictive: observed LAG histogram vs model prediction
edges = np.arange(0, 12, 1)
obs_cnt, _ = np.histogram(lag, bins=edges)
for fam, fit in prim.items():
    probs, sims = postpred_counts(fit['model'], Ages, edges, n_maia,
                                  'attritional', 0.0, 'constant', {})
    # posterior-predictive p for the observed max
    Gg = _cdf_from_density(Ages, observed_density(fit['model'], Ages))
    rngp = np.random.default_rng(2)
    sim_max = np.percentile(ages_draw := np.interp(
        rngp.random((2000, n_maia)), Gg, Ages).max(axis=1), [5, 50, 95])

# ============================================================ 2. Psittacosaurus
dfp = pd.read_csv('../data/processed/psittacosaurus_zhao2013_specimens.csv')
a_psit = dfp['age_numeric'].astype(float).dropna().values  # V14342 (size-only) excluded
ivs_p = [(a, a + 1.0) for a in a_psit]
st_p = [{'type': 'ages', 'intervals': ivs_p}]
psit = {}
for (asm, r_, tag) in [('attritional', 0.0, 'attritional'),
                       ('catastrophic', 0.0, 'standing|r0'),
                       ('catastrophic', -0.10, 'standing|r-0.10'),
                       ('catastrophic', 0.10, 'standing|r+0.10')]:
    res = fit_all(st_p, asm, r_, 'constant', {})
    for fam, fit in res.items():
        rows.append(summarize_fit(f'Psittacosaurus|{tag}', fam, fit))
    psit[tag] = res

# ============================================================ 3. Mammaliaforms
dfn = pd.read_csv('../data/processed/newham2020_cementum_counts.csv')
for tax in ['Morganucodon', 'Kuehneotherium']:
    d = dfn[dfn.taxon == tax]
    obs = d[['observer1', 'observer2', 'observer3']].values.astype(float)
    med = np.median(obs, axis=1)
    iqr_spread = np.ptp(obs, axis=1)
    ivs_m = [(max(0, m - s / 2), m + s / 2 + 0.5) for m, s in zip(med, iqr_spread)]
    st_m = [{'type': 'ages', 'intervals': ivs_m}]
    ages_sm = np.linspace(1e-4, 30, 3500)
    for (asm, r_, tag) in [('attritional', 0.0, 'attritional'),
                           ('catastrophic', 0.0, 'standing|r0')]:
        res = fit_all(st_m, asm, r_, 'constant', {}, ages=ages_sm)
        for fam, fit in res.items():
            rows.append(summarize_fit(f'{tax}|{tag}', fam, fit))

# ============================================================ 4. Albertosaurus grouped lx
emp_lx = np.array([1000, 1000, 954, 954, 909, 909, 864, 864, 818, 773, 773, 727,
                   682, 636, 545, 456, 409, 312, 273, 182, 136, 91, 91, 45, 45,
                   45, 45, 45, 1], float)
n_spec = 22
dx = -np.diff(emp_lx)
counts = np.round(dx / 1000 * n_spec).astype(int)
edges_a = np.arange(0, 30, 1.0)
st_a = [{'type': 'grouped', 'edges': edges_a, 'counts': counts}]
ages_a = np.linspace(1e-4, 35, 4000)
for (asm, r_, tag) in [('attritional', 0.0, 'attritional'),
                       ('catastrophic', 0.0, 'standing|r0')]:
    res = fit_all(st_a, asm, r_, 'constant', {}, ages=ages_a)
    for fam, fit in res.items():
        rows.append(summarize_fit(f'Albertosaurus|{tag}', fam, fit))

out = pd.DataFrame(rows)
out.to_csv('../output/tables/phase6_fossil_fits.csv', index=False)
print(out.groupby('dataset')[['median', 'mean', 'q90', 'E_M50']].describe()
      .loc[:, (slice(None), ['min', 'max'])].round(2).to_string())
print('\nprimary Maiasaura fits:')
print(out[out.dataset == 'Maiasaura|attritional|q_const'].round(2).to_string())
print('Maiasaura n =', n_maia, 'max LAG =', max_maia)
