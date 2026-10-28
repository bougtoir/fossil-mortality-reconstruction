"""Fitting engine: MLE and Bayesian (emcee) fits of latent mortality models
to heterogeneous fossil-like evidence."""
import numpy as np
from scipy.optimize import minimize
from mortality_models import (MortalityModel, observed_density, loglik_ages,
                              loglik_grouped, loglik_max_only, Q_FAMILIES)

# Parametrization: all params strictly positive, fitted on log scale.
FAMILY_PARAMS = {
    'weibull': ['lam', 'k'],
    'gompertz_makeham': ['a', 'b', 'c'],
    'siler': ['a1', 'b1', 'a2', 'a3', 'b3'],
    'piecewise': ['h0', 'h1', 'h2', 'h3', 'h4'],
}

# weakly-informative log-priors: Normal(log_scale_guess, 2) — very broad
PRIOR_MEAN_LOG = {
    'weibull': {'lam': np.log(15), 'k': np.log(2)},
    'gompertz_makeham': {'a': np.log(0.01), 'b': np.log(0.1), 'c': np.log(0.02)},
    'siler': {'a1': np.log(0.5), 'b1': np.log(1.0), 'a2': np.log(0.02),
              'a3': np.log(1e-4), 'b3': np.log(0.2)},
    'piecewise': {f'h{i}': np.log(0.05) for i in range(5)},
}
PRIOR_SD_LOG = 2.5

def make_model(family, xlog, piecewise_edges=None):
    return MortalityModel(family, np.exp(xlog), piecewise_edges)

def study_loglik(g, ages, studies):
    """studies: list of dicts:
      {'type':'ages','intervals':[(lo,hi)]}            # hi=None lower-bound
      {'type':'grouped','edges':[..],'counts':[..]}
      {'type':'max_only','m':m,'n':n}
    """
    ll = 0.0
    for st in studies:
        if st['type'] == 'ages':
            ll += loglik_ages(g, ages, st['intervals'])
        elif st['type'] == 'grouped':
            ll += loglik_grouped(g, ages, np.asarray(st['edges']), np.asarray(st['counts']))
        elif st['type'] == 'max_only':
            ll += loglik_max_only(g, ages, st['m'], st['n'])
    return ll

def build_negloglik(family, ages, studies, assemblage='attritional', r=0.0,
                    q_family='constant', q_kw=None, piecewise_edges=None,
                    prior=PRIOR_SD_LOG):
    def nll(xlog):
        try:
            m = make_model(family, xlog, piecewise_edges)
            g = observed_density(m, ages, assemblage, r, q_family, q_kw)
            if not np.all(np.isfinite(g)) or np.trapezoid(g, ages) < 0.99:
                return 1e10
            ll = study_loglik(g, ages, studies)
            if not np.isfinite(ll):
                return 1e10
            lp = -0.5 * np.sum((xlog / prior) ** 2) if prior else 0.0
            return -(ll + lp)
        except (FloatingPointError, OverflowError, ValueError):
            return 1e10
    return nll

def default_x0(family, piecewise_edges=None):
    return np.array([PRIOR_MEAN_LOG[family][p] for p in FAMILY_PARAMS[family]])

def fit_mle(family, ages, studies, assemblage='attritional', r=0.0,
            q_family='constant', q_kw=None, piecewise_edges=None,
            n_starts=6, seed=0, prior=PRIOR_SD_LOG):
    """Fit with several jittered restarts; return (model, fit_info)."""
    rng = np.random.default_rng(seed)
    nll = build_negloglik(family, ages, studies, assemblage, r, q_family,
                          q_kw, piecewise_edges, prior)
    x0 = default_x0(family, piecewise_edges)
    best = None
    for i in range(n_starts):
        x = x0 + (0 if i == 0 else rng.normal(0, 0.7, x0.size))
        res = minimize(nll, x, method='Nelder-Mead',
                       options={'maxiter': 4000, 'xatol': 1e-4, 'fatol': 1e-6})
        if res.fun < 1e9 and (best is None or res.fun < best.fun):
            best = res
    if best is None or not np.isfinite(best.fun):
        return None, {'converged': False}
    return make_model(family, best.x, piecewise_edges), {
        'converged': bool(best.success or best.fun < 1e9),
        'nll': float(best.fun), 'xlog': best.x}

def sample_posterior(family, ages, studies, assemblage='attritional', r=0.0,
                     q_family='constant', q_kw=None, piecewise_edges=None,
                     n_walkers=24, n_steps=4000, burn=1500, seed=0,
                     prior=PRIOR_SD_LOG, x_start=None):
    """emcee ensemble sampler on log-params with weakly-informative prior."""
    import emcee
    nll = build_negloglik(family, ages, studies, assemblage, r, q_family,
                          q_kw, piecewise_edges, prior)
    ndim = len(FAMILY_PARAMS[family])
    if x_start is None:
        x_start = default_x0(family, piecewise_edges)
    rng = np.random.default_rng(seed)
    p0 = x_start + rng.normal(0, 0.3, (n_walkers, ndim))
    sampler = emcee.EnsembleSampler(n_walkers, ndim, lambda x: -nll(x))
    sampler.run_mcmc(p0, n_steps, progress=False)
    chain = sampler.get_chain(discard=burn, flat=True)
    lnp = sampler.get_log_prob(discard=burn, flat=True)
    acc = float(np.mean(sampler.acceptance_fraction))
    return {'chain': chain, 'logpost': lnp, 'acc': acc,
            'param_names': FAMILY_PARAMS[family]}
