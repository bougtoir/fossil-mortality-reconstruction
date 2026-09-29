"""Phase 7 — sensitivity analyses on the fossil demonstrations.

For each fossil dataset (Maiasaura primary; others secondary):
  - mortality family (weibull / gompertz_makeham / siler / piecewise)
  - q scenario (constant / juv deficit / juv deficit quadratic / logistic)
  - age error (exact vs interval vs +-1 LAG retrocalculation for Maiasaura)
  - youngest/oldest exclusion (drop age-0 / top-10%)
  - n uncertainty (Poisson-jittered n for grouped/max terms)
  - catastrophic r (profile)
  - prior sensitivity (prior sd 1.5 vs 2.5 vs 4 on MLE-penalty)
  - leave-one-study-out not applicable (single study) → leave-one-age-class-out
Output: output/tables/phase7_sensitivity.csv; console summary of materiality.
"""
import numpy as np, pandas as pd, sys
sys.path.insert(0, '.')
from mortality_models import mortality_targets
from fitting import fit_mle
FAMS = ['weibull', 'gompertz_makeham', 'siler']

AGES45 = np.linspace(1e-4, 45, 5000)


def run(tag, studies, assemblage='attritional', r=0.0, qf='constant', qkw=None,
        fams=FAMS, prior=2.5, ages=AGES45, seed=11):
    rows = []
    for fam in fams:
        m, info = fit_mle(fam, ages, studies, assemblage=assemblage, r=r,
                          q_family=qf, q_kw=qkw, seed=seed, n_starts=5,
                          prior=prior)
        if m is None:
            rows.append(dict(analysis=tag, family=fam, fail=True))
            continue
        tg = mortality_targets(m, ages)
        rows.append(dict(analysis=tag, family=fam, fail=False,
                         median=tg['median'], mean=tg['mean_age'],
                         q90=tg['q90'], q95=tg['q95'], E_M50=tg['E_M50'],
                         prime_haz=tg['prime_hazard'],
                         juv_haz=tg['juvenile_hazard'],
                         late_slope=tg['late_hazard_slope'],
                         nll=info['nll']))
    return rows


def maiasaura_studies(diag=0):
    df = pd.read_csv('../data/processed/maiasaura_woodward2015_tibiae.csv')
    lag = pd.to_numeric(df['lag_count'], errors='coerce').dropna().values
    return lag, [{'type': 'ages', 'intervals': [(a + diag, a + 1.0 + diag)
                                                for a in lag]}]


rows = []
lag, st0 = maiasaura_studies()

# baseline
rows += run('baseline', st0)
# model family handled within run (all fams)
# q scenarios
for qn, qf, qkw in [('q_juvdef', 'juvenile_deficit', {'q_adult': 1.0, 'age_full': 3.0}),
                    ('q_juvdef_sq', 'juvenile_deficit_sq', {'q_adult': 1.0, 'age_full': 3.0}),
                    ('q_logistic', 'logistic', {'qmax': 1.0, 'a50': 1.5, 's': 0.5})]:
    rows += run(qn, st0, qf=qf, qkw=qkw)
# age error: retrocalculated +1 inner LAG uncertainty
_, st_plus = maiasaura_studies(diag=1)
rows += run('ageerr_plus1lag', st_plus)
# youngest exclusion (drop age-0 specimens)
lag_nz = lag[lag > 0]
rows += run('exclude_age0', [{'type': 'ages',
            'intervals': [(a, a + 1.0) for a in lag_nz]}])
# oldest exclusion (drop top ~10%)
thr = np.quantile(lag, 0.9)
rows += run('exclude_top10pct', [{'type': 'ages',
            'intervals': [(a, a + 1.0) for a in lag[lag <= thr]]}])
# catastrophic r profile
for r_ in [-0.1, -0.05, 0.0, 0.05, 0.1]:
    rows += run(f'standing_r{r_:+.2f}', st0, assemblage='catastrophic', r=r_)
# prior strength
for ps in [1.5, 4.0]:
    rows += run(f'prior_sd{ps}', st0, prior=ps)
# leave-one-age-class-out
for cls in sorted(set(lag.astype(int))):
    ll = lag[lag.astype(int) != cls]
    rows += run(f'loco_age{cls}', [{'type': 'ages',
                'intervals': [(a, a + 1.0) for a in ll]}])

out = pd.DataFrame(rows)
out.to_csv('../output/tables/phase7_sensitivity.csv', index=False)
piv = out[~out.fail].pivot_table(index='analysis', columns='family',
                                 values='median')
print(piv.round(2).to_string())
print('\nrange of median across analyses (per family):')
print(out[~out.fail].groupby('family')['median'].agg(['min', 'max']).round(2))
