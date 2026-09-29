"""Mortality models, observation processes, and likelihoods for fossil
age-at-death reconstruction.

Latent model: age at death T ~ F with hazard mu(t), survival S(t), density f(t).
Assemblage formation:
  attritional   : base density d(a) = f(a)            (deaths)
  catastrophic  : base density n(a) ∝ S(a) exp(-r a)  (standing crop / living)
Observation   : q_j(a) = P(preserved/recovered/measurable | age a, study j)
  observed g_j(a) ∝ base_j(a) * q_j(a)
Report types  : exact ages | interval ages | lower bounds | grouped counts |
                maximum-only (order statistic of observed dist)
"""
import numpy as np
from scipy.special import gammainc, gamma

# ---------------------------------------------------------------- hazards

def hazard_weibull(t, lam, k):
    t = np.maximum(np.asarray(t, dtype=float), 1e-9)
    return (k / lam) * (t / lam) ** (k - 1)

def cumhaz_weibull(t, lam, k):
    return (t / lam) ** k

def hazard_gompertz_makeham(t, a, b, c):
    return c + a * np.exp(b * t)

def cumhaz_gompertz_makeham(t, a, b, c):
    return c * t + (a / b) * (np.exp(b * t) - 1.0)

def hazard_siler(t, a1, b1, a2, a3, b3):
    return a1 * np.exp(-b1 * t) + a2 + a3 * np.exp(b3 * t)

def cumhaz_siler(t, a1, b1, a2, a3, b3):
    return (a1 / b1) * (1.0 - np.exp(-b1 * t)) + a2 * t + (a3 / b3) * (np.exp(b3 * t) - 1.0)

def hazard_piecewise(t, edges, rates):
    """edges: (nbins+1,) bin boundaries incl. 0; rates: (nbins,) constant hazard per bin."""
    idx = np.clip(np.searchsorted(edges, t, side='right') - 1, 0, len(rates) - 1)
    return np.asarray(rates)[idx]

def cumhaz_piecewise(t, edges, rates):
    edges = np.asarray(edges); rates = np.asarray(rates)
    widths = np.diff(edges)
    cum = np.concatenate([[0.0], np.cumsum(rates * widths)])
    idx = np.clip(np.searchsorted(edges, t, side='right') - 1, 0, len(rates) - 1)
    return cum[idx] + rates[idx] * (np.asarray(t) - edges[idx])

HAZARDS = {
    'weibull': (hazard_weibull, cumhaz_weibull),
    'gompertz_makeham': (hazard_gompertz_makeham, cumhaz_gompertz_makeham),
    'siler': (hazard_siler, cumhaz_siler),
    'piecewise': (hazard_piecewise, cumhaz_piecewise),
}


class MortalityModel:
    """Hazard-parameterized latent mortality distribution."""

    def __init__(self, family, params, piecewise_edges=None):
        self.family = family
        self.params = tuple(np.atleast_1d(params))
        self.edges = piecewise_edges
        if family == 'piecewise':
            assert piecewise_edges is not None
            self._h = lambda t: hazard_piecewise(t, piecewise_edges, self.params)
            self._H = lambda t: cumhaz_piecewise(t, piecewise_edges, self.params)
        else:
            h, H = HAZARDS[family]
            self._h = lambda t: h(t, *self.params)
            self._H = lambda t: H(t, *self.params)

    def hazard(self, t):
        return self._h(np.asarray(t, dtype=float))

    def cumhaz(self, t):
        return self._H(np.asarray(t, dtype=float))

    def S(self, t):
        return np.exp(-self.cumhaz(t))

    def f(self, t):
        return self.hazard(t) * self.S(t)


def standing_density(model, ages, r=0.0):
    """Standing-crop (catastrophic) density proportional to S(a) e^{-ra}."""
    w = model.S(ages) * np.exp(-r * ages)
    return w / np.trapezoid(w, ages)


def death_density(model, ages):
    w = model.f(ages)
    return w / np.trapezoid(w, ages)


# ------------------------------------------------------- observation q(a)

def q_constant(ages, p=1.0):
    return np.full_like(ages, p, dtype=float)

def q_logistic(ages, qmax, a50, s):
    """Monotone increasing detectability: qmax * logistic((a - a50)/s)."""
    z = (ages - a50) / np.maximum(s, 1e-6)
    return qmax / (1.0 + np.exp(-z))

def q_juvenile_deficit(ages, q_adult, age_full, ramp='linear'):
    """q(a) = q_adult for a >= age_full; ramped-up detection below."""
    q = np.full_like(ages, q_adult, dtype=float)
    young = ages < age_full
    if ramp == 'linear':
        q[young] = q_adult * ages[young] / age_full
    elif ramp == 'quadratic':
        q[young] = q_adult * (ages[young] / age_full) ** 2
    return q

def q_saturating(ages, qmax, rate):
    return qmax * (1.0 - np.exp(-rate * ages))

Q_FAMILIES = {
    'constant': lambda a, **kw: q_constant(a, **kw),
    'logistic': lambda a, **kw: q_logistic(a, **kw),
    'juvenile_deficit': lambda a, **kw: q_juvenile_deficit(a, **kw),
    'juvenile_deficit_sq': lambda a, **kw: q_juvenile_deficit(a, ramp='quadratic', **kw),
    'saturating': lambda a, **kw: q_saturating(a, **kw),
    'nonmonotone': lambda a, q_max=1.0, a_pk=2.0, w=1.0, **kw: q_max * np.exp(-((a - a_pk) / w) ** 2),
}


def observed_density(model, ages, assemblage='attritional', r=0.0,
                     q_family='constant', q_kw=None):
    base = (death_density(model, ages) if assemblage == 'attritional'
            else standing_density(model, ages, r))
    q = Q_FAMILIES[q_family](ages, **(q_kw or {}))
    g = base * q
    tot = np.trapezoid(g, ages)
    if not np.isfinite(tot) or tot <= 0:
        return np.full_like(ages, np.nan)
    return g / tot


# ------------------------------------------------------------ likelihoods

def _cdf_from_density(ages, g):
    return np.concatenate([[0.0], np.cumsum((g[:-1] + g[1:]) / 2.0 * np.diff(ages))])

def loglik_ages(g, ages, obs):
    """obs: array of (lo, hi) age intervals; exact age => lo=hi handled as
    density at age via interpolation."""
    G = _cdf_from_density(ages, g)
    ll = 0.0
    for lo, hi in obs:
        if hi is None or np.isinf(hi):          # lower bound: T >= lo
            p = 1.0 - np.interp(lo, ages, G)
        elif lo is None or lo <= 0 and hi <= 0: # T in [0,hi]
            p = np.interp(hi, ages, G)
        elif hi == lo:                          # exact
            p = np.interp(lo, ages, g)
        else:                                   # interval
            p = np.interp(hi, ages, G) - np.interp(lo, ages, G)
        ll += np.log(max(p, 1e-300))
    return ll

def loglik_grouped(g, ages, edges, counts):
    """counts[i] specimens aged in [edges[i], edges[i+1])."""
    G = _cdf_from_density(ages, g)
    lo = np.interp(edges[:-1], ages, G)
    hi = np.interp(edges[1:], ages, G)
    p = np.clip(hi - lo, 1e-300, None)
    return float(np.sum(counts * np.log(p)))

def loglik_max_only(g, ages, m, n):
    """Maximum-only report: observed max m among n draws from g.
    Continuous order-statistic density n g(m) G(m)^{n-1}."""
    G = _cdf_from_density(ages, g)
    gm = np.interp(m, ages, g)
    Gm = np.interp(m, ages, G)
    if Gm <= 0:
        return -np.inf
    return np.log(n) + np.log(max(gm, 1e-300)) + (n - 1) * np.log(Gm)

def expected_max(g, ages, n):
    """E[M_n] for draws from g."""
    G = _cdf_from_density(ages, g)
    # E[M_n] = int_0^A (1 - G(a)^n) da  (non-negative variable)
    return float(np.trapezoid(1.0 - G ** n, ages))


# ------------------------------------------------------------- targets

def mortality_targets(model, ages):
    """Summary quantities of the latent mortality distribution."""
    g = death_density(model, ages)
    G = _cdf_from_density(ages, g)
    S = 1.0 - G
    mu = model.hazard(ages)
    out = {}
    # quantiles
    for q, name in [(0.5, 'median'), (0.9, 'q90'), (0.95, 'q95')]:
        idx = np.searchsorted(G, q)
        out[name] = float(ages[min(idx, len(ages) - 1)])
    # mean age at death
    out['mean_age'] = float(np.trapezoid(ages * g, ages))
    # juvenile hazard: mean hazard ages 0-10% of max
    a_juv = ages[-1] * 0.1
    jmask = ages <= a_juv
    out['juvenile_hazard'] = float(np.trapezoid(mu[jmask], ages[jmask]) / a_juv)
    # prime-age hazard: mean hazard middle 20-60% of lifespan
    pm = (ages > ages[-1] * 0.2) & (ages < ages[-1] * 0.6)
    out['prime_hazard'] = float(np.mean(mu[pm]))
    # late-life hazard slope: d log mu / da over last 40% of ages
    lm = ages > ages[-1] * 0.6
    if lm.sum() > 5:
        lg = np.log(np.clip(mu[lm], 1e-12, None))
        out['late_hazard_slope'] = float(np.polyfit(ages[lm], lg, 1)[0])
    # age of hazard minimum
    out['hazard_min_age'] = float(ages[np.argmin(mu)])
    # standardized expected maxima
    for nn in (50, 100):
        out[f'E_M{nn}'] = expected_max(g, ages, nn)
    return out
