"""Fossilization operators: turn a perfect extant life table into a sparse,
biased, coarsely-reported fossil-like sample."""
import numpy as np
from mortality_models import Q_FAMILIES


class LifeTable:
    """Empirical latent mortality from a malddaba life table (yearly lx)."""
    def __init__(self, age, lx):
        self.age = np.asarray(age, float)
        self.lx = np.asarray(lx, float)
        d = -np.diff(self.lx, append=self.lx[-1] * 0.0)
        d[-1] = max(self.lx[-1], 0.0)          # last bin: all remaining die
        self.death_pdf = d / d.sum()           # prob mass of death in [x, x+1)
        self.Amax = float(self.age[-1]) + 1.0

    def sample_deaths(self, n, rng):
        x = rng.choice(self.age, size=n, p=self.death_pdf)
        return x + rng.random(n)

    def sample_standing(self, n, rng, r=0.0):
        # standing crop ages ~ S(a) e^{-r a}, continuous within year
        w = self.lx * np.exp(-r * self.age)
        w = w / w.sum()
        x = rng.choice(self.age, size=n, p=w)
        return x + rng.random(n)

    def targets(self):
        F = np.cumsum(self.death_pdf)
        med = np.interp(0.5, F, self.age)
        q90 = np.interp(0.9, F, self.age)
        q95 = np.interp(0.95, F, self.age)
        mean = float(np.sum(self.death_pdf * (self.age + 0.5)))
        # continuous-ish CDF for E[M_n]: step F over [age, age+1)
        grid = np.linspace(0, self.Amax + 1, 4001)
        Fg = np.interp(grid, np.append(self.age, self.Amax),
                       np.append(F, 1.0))
        e50 = float(np.trapezoid(1.0 - Fg ** 50, grid))
        return dict(median=med, q90=q90, q95=q95, mean_age=mean, E_M50=e50)


# -- preservation q scenarios (params scaled to each species' lifespan) ------
def q_params(q_name, Amax):
    """Return (q_family, q_kw) for a scenario, scaled to species support."""
    return {
        'constant':  ('constant', {}),
        'juv_moderate': ('juvenile_deficit', {'q_adult': 1.0, 'age_full': 0.20 * Amax}),
        'juv_severe':   ('juvenile_deficit', {'q_adult': 1.0, 'age_full': 0.35 * Amax}),
        'monotone_logistic': ('logistic', {'qmax': 1.0, 'a50': 0.15 * Amax, 's': 0.05 * Amax}),
        'nonmonotone': ('nonmonotone', {'q_max': 1.0, 'a_pk': 0.45 * Amax, 'w': 0.30 * Amax}),
    }[q_name]

Q_SCENARIOS = {k: None for k in
               ('constant', 'juv_moderate', 'juv_severe', 'monotone_logistic', 'nonmonotone')}


def simulate_study(lt: LifeTable, n, rng, assemblage='attritional', r=0.0,
                   q_name='constant', resolution='exact',
                   reporting='all', amax_q=None):
    """Return a studies list for fitting.py, plus the kept raw ages."""
    # 1) draw ages from the assemblage process (oversample to allow rejection)
    pool = 5 * n
    ages_true = (lt.sample_deaths(pool, rng) if assemblage == 'attritional'
                 else lt.sample_standing(pool, rng, r))
    # 2) preservation/recovery rejection sampling
    qf, qkw = q_params(q_name, lt.Amax)
    qv = Q_FAMILIES[qf](ages_true, **qkw)
    keep = rng.random(pool) < qv
    a = ages_true[keep][:n]
    n_eff = a.size

    # 3) age-measurement resolution → intervals (lo, hi)
    def to_int(x, res):
        if res == 'exact':
            return (x, x)
        if res == 'rounded':
            return (np.floor(x), np.floor(x) + 1.0)
        if res == 'interval2':
            lo = 2.0 * np.floor(x / 2.0)
            return (lo, lo + 2.0)
        if res == 'noisy':
            lo, hi = sorted((max(0.0, x * np.exp(rng.normal(0, 0.10))),
                             max(0.0, x * np.exp(rng.normal(0, 0.10)))))
            return (lo, hi)
        raise ValueError(res)

    if reporting == 'all':
        ivs = [to_int(x, resolution) for x in a]
        return [{'type': 'ages', 'intervals': ivs}], a
    if reporting == 'grouped':
        edges = np.arange(0.0, lt.Amax + 2.0, 2.0)
        cnt, _ = np.histogram(a, bins=edges)
        return [{'type': 'grouped', 'edges': edges, 'counts': cnt}], a
    if reporting == 'max_only':
        m = float(np.max([to_int(x, resolution)[1] for x in a])) if n_eff else np.nan
        return [{'type': 'max_only', 'm': m, 'n': n_eff}], a
    if reporting == 'mixed':
        # n-1 individuals reported, plus a literature maximum from an
        # independent sample of n_lit specimens (no double counting)
        ivs = [to_int(x, resolution) for x in a[:-1]]
        n_lit = 30
        a2 = (lt.sample_deaths(n_lit, rng) if assemblage == 'attritional'
              else lt.sample_standing(n_lit, rng, r))
        m = float(a2.max())
        return [{'type': 'ages', 'intervals': ivs},
                {'type': 'max_only', 'm': m, 'n': n_lit}], a
    raise ValueError(reporting)
