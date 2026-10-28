"""Canonical results access layer.

Every analysis-derived value consumed by the manuscript, supplement,
figure and table builders comes through this module (or is read directly
from output/tables/*). No result number is ever typed into prose by hand.

Usage:
    from canonical_results import results
    r = results()
    r['emax']['E_M5']            # scalar from phase5_expected_maxima.json
    r['n_maia']                  # 49, counted from data/processed CSV
    r['cem_med_rng']             # (min, max) attritional cementum medians
"""
import json
import numpy as np
import pandas as pd
from paths import TABLES, DATA_PROCESSED

TAB = TABLES
PROC = DATA_PROCESSED


def _t(name):
    return pd.read_csv(TAB / name)


def _j(name):
    return json.loads((TAB / name).read_text())


def load_tables():
    return {
        'rec': _t('recoverability_map.csv'),
        'rec_raw': _t('recoverability_map_raw.csv'),
        'phase5': _t('phase5_model_comparison.csv'),
        'emax': _j('phase5_expected_maxima.json'),
        'foss': _t('phase6_fossil_fits.csv'),
        'post': _t('phase6b_posterior.csv'),
        'sens': _t('phase7_sensitivity.csv'),
        'rprof': _t('identifiability_r_profile.csv'),
        'isum': _j('identifiability_summary.json'),
        'qsc': _t('identifiability_q_scenarios.csv'),
    }


def dataset_rows(tables, pattern):
    return tables['foss'][tables['foss'].dataset.str.contains(pattern)]


def results():
    """One canonical dict of every analysis-derived scalar the prose uses."""
    t = load_tables()
    foss = t['foss']
    maia = foss[foss.dataset.str.startswith('Maiasaura|attritional|q_const')]
    sens = t['sens']
    p5 = t['phase5'].groupby('model')['median'].agg(['mean', 'std'])
    emax = t['emax']

    lag = pd.to_numeric(
        pd.read_csv(PROC / 'maiasaura_woodward2015_tibiae.csv')['lag_count'],
        errors='coerce').dropna()
    psit_n = int(pd.read_csv(PROC / 'psittacosaurus_zhao2013_specimens.csv')
                 ['age_numeric'].astype(float).dropna().size)
    cem = pd.read_csv(PROC / 'newham2020_cementum_counts.csv')
    cem_n = {k: int(v) for k, v in cem.taxon.value_counts().items()}
    alb = pd.read_csv(PROC / 'albertosaurus_griebeler2021_lx.csv')

    focal = ['Suricata_suricatta', 'Cervus_elaphus', 'Loxodonta_africana']
    rec = t['rec']
    cem_attr = dataset_rows(t, 'Morganucodon|Kuehneotherium')
    cem_attr = cem_attr[cem_attr.dataset.str.endswith('attritional')]
    alb_rows = dataset_rows(t, 'Albertosaurus')
    psit_rows = dataset_rows(t, 'Psittacosaurus')
    excl0 = sens[sens.analysis == 'exclude_age0']

    return {
        'tables': t,
        'emax': emax,
        'p5': p5,
        'post': t['post'],
        # --- fossil dataset sizes (counted from data, never typed) ---
        'n_maia': int(len(lag)),
        'max_maia_lag': float(lag.max()),
        'n_psit': psit_n,
        'cem_n': cem_n,
        'n_alberto_specimens': 22,   # Erickson sample size behind the lx table
        'n_alberto_lx_points': int(len(alb)),
        'n_lifetables': int(len(pd.read_csv(PROC / 'malddaba_populations.csv'))),
        # --- manuscript value ranges ---
        'maia_med_rng': (maia['median'].min(), maia['median'].max()),
        'sens_med_rng': (sens[~sens.fail]['median'].min(),
                         sens[~sens.fail]['median'].max()),
        'excl_age0_median_mean': float(excl0['median'].mean()),
        'psit_mean_rng': (psit_rows['mean'].min(), psit_rows['mean'].max()),
        'alb_q90_rng': (alb_rows['q90'].min(), alb_rows['q90'].max()),
        'alb_med_rng': (alb_rows['median'].min(), alb_rows['median'].max()),
        'cem_med_rng': (cem_attr['median'].min(), cem_attr['median'].max()),
        # --- recoverability summary biases ---
        'maxonly_med_bias': float(
            rec[(rec.reporting == 'max_only') & rec.species.isin(focal)
                & (rec.analyst == 'informed')]['median_bias'].mean()),
        'q_naive_bias': float(
            rec[(rec.q == 'juv_severe') & (rec.analyst == 'naive')
                & rec.species.isin(focal)]['median_bias'].mean()),
        'q_inform_bias': float(
            rec[(rec.q == 'juv_severe') & (rec.analyst == 'informed')
                & rec.species.isin(focal)]['median_bias'].mean()),
        'n_fits': int(len(t['rec_raw'])),
        'true_median': float(emax['true_median']),
    }


def yr(x, digits=1):
    """Format an age in years."""
    return f'{x:.{digits}f}'


def yr_range(rng, digits=0, approx=True):
    """Format a (min, max) year range like '~4–11'."""
    lo, hi = rng
    s = f'{lo:.{digits}f}\u2013{hi:.{digits}f}'
    return f'~{s}' if approx else s
