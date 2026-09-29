"""Phase 4 — extant-to-fossil degradation experiment.

Truth: malddaba empirical life tables. Degrade per scenario; fit Weibull MLE
under 'naive' (attritional + constant q + exact likelihood) and 'informed'
(correct assemblage/q/resolution, r assumed known) analysts. Metrics per cell:
bias, RMSE, spread (P5-P95), failure freq on latent targets.
Output: output/tables/recoverability_map.csv (+ raw per-rep estimates).
"""
import numpy as np, pandas as pd, sys, itertools, json
from multiprocessing import Pool
sys.path.insert(0, '.')
from degrade import LifeTable, simulate_study, q_params
from fitting import fit_mle
from mortality_models import mortality_targets

TARGETS = ['median', 'mean_age', 'q90', 'q95', 'E_M50',
           'juvenile_hazard', 'prime_hazard', 'late_hazard_slope', 'hazard_min_age']

AGE_GRID_CACHE = {}
def age_grid(Amax):
    if Amax not in AGE_GRID_CACHE:
        AGE_GRID_CACHE[Amax] = np.linspace(1e-4, Amax * 1.15, 4001)
    return AGE_GRID_CACHE[Amax]

LT_CACHE = {}
def life_table(species):
    if species in LT_CACHE:
        return LT_CACHE[species]
    df = pd.read_csv('../data/processed/malddaba_life_tables.csv')
    d = df[df.species == species].sort_values('Age')
    lt = LifeTable(d.Age.values, d.lx.values)
    LT_CACHE[species] = lt
    return lt

def run_cell(species, n, resolution, q_name, reporting, assemblage, r,
             rep, analyst):
    import zlib
    seed = zlib.crc32(repr((species, n, resolution, q_name, reporting,
                          assemblage, r, rep, analyst)).encode())
    rng = np.random.default_rng(seed)
    lt = life_table(species)
    studies, kept = simulate_study(lt, n, rng, assemblage, r, q_name,
                                 resolution, reporting)
    n_eff = len(kept)
    if n_eff < 3:
        return dict(species=species, n=n, n_eff=n_eff, resolution=resolution,
                    q=q_name, reporting=reporting, assemblage=assemblage, r=r,
                    rep=rep, analyst=analyst, fail=True)
    if analyst == 'naive':
        kw = dict(assemblage='attritional', r=0.0, q_family='constant', q_kw={})
        st = [{'type': 'ages' if s['type'] != 'max_only' else 'max_only',
               **{k: v for k, v in s.items() if k != 'type'}} for s in studies]
        # naive analyst collapses intervals to midpoints (treats as exact)
        st = []
        for s in studies:
            if s['type'] == 'ages':
                st.append({'type': 'ages',
                           'intervals': [((lo + hi) / 2, (lo + hi) / 2)
                                         for lo, hi in s['intervals']]})
            else:
                st.append(s)
        studies_fit = st
    else:
        qf, qkw = q_params(q_name, lt.Amax)
        kw = dict(assemblage=assemblage, r=r if assemblage == 'catastrophic' else 0.0,
                  q_family=qf, q_kw=qkw)
        studies_fit = studies
    ages = age_grid(lt.Amax)
    m, info = fit_mle('weibull', ages, studies_fit, seed=rep, n_starts=4, **kw)
    if m is None:
        return dict(species=species, n=n, n_eff=n_eff, resolution=resolution,
                    q=q_name, reporting=reporting, assemblage=assemblage, r=r,
                    rep=rep, analyst=analyst, fail=True)
    tg = mortality_targets(m, ages)
    row = dict(species=species, n=n, n_eff=n_eff, resolution=resolution,
               q=q_name, reporting=reporting, assemblage=assemblage, r=r,
               rep=rep, analyst=analyst, fail=False,
               lam=m.params[0], k=m.params[1])
    row.update(tg)
    return row


def build_jobs():
    jobs = []
    # focal species: short/medium/long-lived representatives
    FOCAL = ['Suricata_suricatta', 'Cervus_elaphus', 'Loxodonta_africana']
    BASE = dict(resolution='exact', q_name='constant', reporting='all',
                assemblage='attritional', r=0.0)
    REPS = 40
    for sp in FOCAL:
        # n sweep
        for n in [5, 10, 20, 30, 50, 100]:
            for rep in range(REPS):
                for an in ['naive', 'informed']:
                    jobs.append((sp, n, BASE['resolution'], BASE['q_name'],
                                 BASE['reporting'], BASE['assemblage'],
                                 BASE['r'], rep, an))
        # factor sweeps at n=20 and n=50
        for n in [20, 50]:
            for res in ['rounded', 'interval2', 'noisy']:
                for rep in range(REPS):
                    for an in ['naive', 'informed']:
                        jobs.append((sp, n, res, BASE['q_name'], BASE['reporting'],
                                     BASE['assemblage'], BASE['r'], rep, an))
            for qn in ['juv_moderate', 'juv_severe', 'monotone_logistic', 'nonmonotone']:
                for rep in range(REPS):
                    for an in ['naive', 'informed']:
                        jobs.append((sp, n, BASE['resolution'], qn, BASE['reporting'],
                                     BASE['assemblage'], BASE['r'], rep, an))
            for rp_ in ['grouped', 'max_only', 'mixed']:
                for rep in range(REPS):
                    for an in ['naive', 'informed']:
                        jobs.append((sp, n, BASE['resolution'], BASE['q_name'], rp_,
                                     BASE['assemblage'], BASE['r'], rep, an))
            for (asm, r) in [('catastrophic', 0.0), ('catastrophic', -0.05),
                             ('catastrophic', 0.05)]:
                for rep in range(REPS):
                    for an in ['naive', 'informed']:
                        jobs.append((sp, n, BASE['resolution'], BASE['q_name'],
                                     BASE['reporting'], asm, r, rep, an))
    # species diversity sweep: all populations, baseline scenario
    allsp = pd.read_csv('../data/processed/malddaba_populations.csv').species.unique()
    for sp in allsp:
        for rep in range(30):
            for an in ['naive', 'informed']:
                jobs.append((sp, 30, 'exact', 'constant', 'all',
                             'attritional', 0.0, rep, an))
    return jobs


def worker(j):
    try:
        return run_cell(*j)
    except Exception as e:
        (sp, n, res, qn, rp_, asm, r, rep, an) = j
        return dict(species=sp, n=n, resolution=res, q=qn, reporting=rp_,
                    assemblage=asm, r=r, rep=rep, analyst=an, fail=True,
                    error=str(e)[:120])


def summarize(df):
    rows = []
    keys = ['species', 'n', 'resolution', 'q', 'reporting', 'assemblage', 'r', 'analyst']
    lt_cache = {}
    for k, g in df.groupby(keys):
        d = dict(zip(keys, k))
        sp = d['species']
        if sp not in lt_cache:
            lt_cache[sp] = life_table(sp).targets()
        tv = lt_cache[sp]
        ok = g[~g.fail]
        d['n_cells'] = len(g); d['n_fail'] = int(g.fail.sum())
        d['fail_freq'] = float(g.fail.mean()); d['n_eff_mean'] = float(g.n_eff.mean())
        for t in ['median', 'mean_age', 'q90', 'q95', 'E_M50']:
            est = ok[t].values
            if est.size:
                d[f'{t}_bias'] = float(np.mean(est - tv[t]))
                tvv = max(tv[t], 0.5)  # floor at 0.5 yr: relbias meaningless for median≈0 infant-heavy tables
                d[f'{t}_relbias'] = float(np.mean((est - tv[t]) / tvv))
                d[f'{t}_rmse_rel'] = float(np.sqrt(np.mean(((est - tv[t]) / tvv) ** 2)))
                d[f'{t}_p5'] = float(np.percentile(est, 5))
                d[f'{t}_p95'] = float(np.percentile(est, 95))
                d[f'{t}_true'] = float(tv[t])
        rows.append(d)
    return pd.DataFrame(rows)


if __name__ == '__main__':
    jobs = build_jobs()
    print('jobs:', len(jobs))
    with Pool(8) as p:
        res = p.map(worker, jobs, chunksize=20)
    df = pd.DataFrame(res)
    df.to_csv('../output/tables/recoverability_map_raw.csv', index=False)
    summ = summarize(df)
    summ.to_csv('../output/tables/recoverability_map.csv', index=False)
    print('fail rate overall:', round(df.fail.mean(), 3))
    print(summ.groupby(['analyst'])[['median_relbias', 'median_rmse_rel',
                                     'mean_age_relbias']].mean().round(3))
