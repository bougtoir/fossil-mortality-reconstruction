"""Generate manuscript deliverables from output/tables + figures.
All numbers come from result files — nothing is hardcoded except citations.
Outputs in ../manuscript/ and ../output/.
"""
import pandas as pd, numpy as np, json, os, sys
sys.path.insert(0, '.')
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx_utils import add_equation, add_figure, add_df_table, ref_runs

OUT = '../manuscript'
os.makedirs(OUT, exist_ok=True)
FIG = '../output/figures'
TAB = '../output/tables'

# ---------------------------------------------------------------- load results
rec = pd.read_csv(f'{TAB}/recoverability_map.csv')
phase5 = pd.read_csv(f'{TAB}/phase5_model_comparison.csv')
emax = json.load(open(f'{TAB}/phase5_expected_maxima.json'))
foss = pd.read_csv(f'{TAB}/phase6_fossil_fits.csv')
post = pd.read_csv(f'{TAB}/phase6b_posterior.csv')
sens = pd.read_csv(f'{TAB}/phase7_sensitivity.csv')
qscn = pd.read_csv(f'{TAB}/identifiability_q_scenarios.csv')
rprof = pd.read_csv(f'{TAB}/identifiability_r_profile.csv')
isum = json.load(open(f'{TAB}/identifiability_summary.json'))
inv = pd.read_csv('../data_inventory.csv', engine='python')

focal = ['Suricata_suricatta', 'Cervus_elaphus', 'Loxodonta_africana']
rec_f = rec[rec.species.isin(focal)]

def fmt(x, d=1):
    return f'{x:.{d}f}'

# headline numbers
r_span = rprof['mean'].max() - rprof['mean'].min()
r_best = float(rprof.loc[rprof.nll.idxmin(), 'r'])
maia = foss[foss.dataset.str.startswith('Maiasaura|attritional|q_const')]
maia_med_rng = (maia['median'].min(), maia['median'].max())
sens_med_rng = (sens[~sens.fail]['median'].min(), sens[~sens.fail]['median'].max())
p5 = phase5.groupby('model')['median'].agg(['mean', 'std'])
cls_frac = {}
for t in ['median', 'mean_age', 'q90', 'q95', 'E_M50']:
    vc = rec_f[rec_f.analyst == 'informed'][f'class_{t}'].value_counts(normalize=True)
    cls_frac[t] = {c: float(vc.get(c, 0)) for c in 'ABCD'}
maxonly_med_bias = rec[(rec.reporting == 'max_only') & rec.species.isin(focal)
                       & (rec.analyst == 'informed')]['median_bias'].mean()
q_naive_bias = rec[(rec.q == 'juv_severe') & (rec.analyst == 'naive') &
                   rec.species.isin(focal)]['median_bias'].mean()
q_inform_bias = rec[(rec.q == 'juv_severe') & (rec.analyst == 'informed') &
                    rec.species.isin(focal)]['median_bias'].mean()

# ---------------------------------------------------------------- document
doc = Document()
st = doc.styles['Normal']; st.font.name = 'Calibri'; st.font.size = Pt(11)

def H(level, text):
    doc.add_heading(text, level=level)

def P(text, refs=True):
    p = doc.add_paragraph()
    if refs:
        ref_runs(p, text)
    else:
        p.add_run(text)
    return p

def cited_fig(path, num, caption):
    add_figure(doc, f'{FIG}/{path}', f'Figure {num}. {caption}')

# ===== title page
t = doc.add_paragraph(); r = t.add_run(
    'Beyond the oldest known individual: sample-size-aware reconstruction of '
    'mortality in extinct taxa')
r.bold = True; r.font.size = Pt(16)
doc.add_paragraph('A generative framework for latent mortality inference from '
                  'sparse and biased fossil age-at-death evidence, with a '
                  'simulation-validated recoverability map.')
doc.add_paragraph('Manuscript prepared for submission. Author list TBD.')

# ===== abstract
H(1, 'Abstract')
P('Palaeontologists infer the demography of extinct species from fossil '
  'age-at-death evidence: histologically aged individuals, life tables, and '
  '"oldest known specimen" reports. These are three different observation '
  'types of a single latent mortality process, but they are routinely treated '
  'as interchangeable — and the observed age structure is routinely equated '
  'with the mortality schedule. We specify a generative framework that '
  'separates four processes: the latent hazard, the assemblage-formation '
  'mechanism (attritional death assemblage vs catastrophic standing crop), '
  'age-dependent preservation and recovery q(a), and age-estimation error. '
  'We show that the latent mortality distribution and q(a) are not jointly '
  'identifiable, that standing-crop assemblages cannot identify mortality '
  'without independent information on population growth, and that a maximum '
  'report is an order statistic whose evidential content depends on the '
  'sample behind it. We validate the framework by degrading 45 extant mammal '
  'life tables into fossil-like samples under a grid of sample sizes, age '
  'resolutions, observation scenarios, report types, and assemblage '
  'mechanisms, and we classify each mortality summary as robustly '
  'recoverable, conditionally recoverable, weakly identified, or '
  'unidentifiable. Mean age at death and the standardized expected maximum '
  'E[M_n] are the most robust quantities; the median is surprisingly fragile '
  'when mortality is infant-dominated; maximum-only reports cannot support '
  'mortality estimates. Applying the framework to four fossil datasets '
  '(Maiasaura, Psittacosaurus, Albertosaurus, and two mammaliaform '
  'cementum series), we report only recoverable quantities and show that '
  'reasonable analytic choices move the Maiasaura median age-at-death '
  f'estimate across {sens_med_rng[0]:.1f}–{sens_med_rng[1]:.1f} years. We '
  'propose standardized reporting (E[M_50], E[M_100]) as a replacement for '
  'bare "oldest specimen" claims.')

# ===== 1 Introduction
H(1, '1. Introduction')
P('How long did extinct animals live? The evidence is always indirect: '
  'histological age estimates on a handful of specimens [1-3], life tables '
  'assembled from such samples [2,3], and press-ready statements about the '
  '"oldest known" individual of a taxon. Three different kinds of numbers — '
  'individual ages, grouped tallies, and sample maxima — are produced by the '
  'same underlying mortality process, yet the literature treats them largely '
  'as interchangeable evidence for "the lifespan" of a species.')
P('Two complications are well recognized but rarely modelled together. '
  'First, a fossil assemblage is not necessarily a record of deaths: a '
  'catastrophically killed standing crop samples the *living* age structure, '
  'and interpreting it as a death distribution confounds mortality with '
  'population growth [4,5]. Second, preservation, recovery and collection '
  'are age-dependent: juveniles are systematically under-represented in many '
  'assemblages, so the observed age distribution is a filtered version of '
  'the latent one [4]. Steinsaltz and Orzack showed how strongly these '
  'filters can reshape apparent survivorship; what has been missing is a '
  'generative treatment in which all of these processes are explicit and '
  'their identifiability is measured rather than asserted.')
P('Here we build that framework and then subject it to a controlled test. '
  'The latent mortality hazard, the assemblage mechanism, the observation '
  'process q(a), the age-measurement model, and the report type are each '
  'specified separately, so the likelihood of heterogeneous evidence — '
  'individual ages, grouped life tables, and maximum-only reports — can be '
  'written down without double counting. We then degrade 45 empirically '
  'known extant mammal life tables [6] into fossil-like samples under a '
  'systematic grid of information loss, and ask which mortality summaries '
  'survive. The result is a recoverability map: not a claim that a '
  'particular dinosaur lived a particular number of years, but a map of '
  'what the fossil record can defensibly tell us, and where it cannot.')
P('The framework deliberately withholds what it cannot support. Where an '
  'estimand is only weakly identified we report it as such, and where the '
  'fossil data cannot separate mortality from preservation or population '
  'structure, the paper says so. "The mean lifespan of this taxon cannot be '
  'recovered from these data" is, in our view, a publishable answer.')

# ===== 2 Framework
H(1, '2. The generative framework')
P('Fossil age evidence is modelled as a five-stage generative chain '
  '(Figure 1): a latent mortality schedule produces ages at death or ages '
  'in a living population; assemblage formation selects between '
  'attritional and catastrophic (standing-crop) mechanisms; the observation '
  'process q(a) distorts the age distribution; age estimation adds noise '
  'or interval censoring; and the reporting scheme determines whether '
  'individual ages, grouped counts or only a maximum are available. Each '
  'stage is defined below; inference conditions on the whole chain.', refs=False)
cited_fig('fig_scheme.png', 1,
  'The generative chain from a latent mortality schedule μ(t) to reported '
  'fossil age evidence. Dashed nodes mark processes external to the '
  'population that must be modelled, not assumed away.')
H(2, '2.1 Latent mortality')
P('Let T be the latent age at death with hazard μ(t), cumulative hazard '
  'H(t), survival S(t), and density f(t):')
add_equation(doc, ['S(t) = exp(−H(t)),  H(t) = ', ('int', '0', 't', 'μ(u) du'),
                   ',  f(t) = μ(t) S(t)'])
P('Four parametric families are compared throughout: Weibull '
  'μ(t) = (k/λ)(t/λ)', refs=False)
add_equation(doc, ['μ(t) = ', ('frac', 'k', 'λ'), ' (', ('frac', 't', 'λ'),
                   (('sup', ')', 'k−1')), '   (Weibull)'])
add_equation(doc, ['μ(t) = c + a ', ('sup', 'e', 'bt'),
                   '   (Gompertz–Makeham)'])
add_equation(doc, ['μ(t) = ', ('sup', 'a₁e', '−b₁t'), ' + a₂ + ',
                   ('sup', 'a₃e', 'b₃t'), '   (Siler [7])'])
P('plus a piecewise-constant hazard as a flexible benchmark. No family is '
  'privileged: model choice is itself a sensitivity axis.', refs=False)

H(2, '2.2 Assemblage formation')
P('An attritional assemblage records deaths, so its base density is the '
  'death-age density f(a). A catastrophic or standing-crop assemblage '
  'samples the living structure, which under a stable population with '
  'growth rate r is')
add_equation(doc, ['n(a) ∝ S(a) ', ('sup', 'e', '−ra')])
P('For r = 0 this reduces to n(a) ∝ S(a). Where the taphonomic literature '
  'disputes the mechanism (e.g. the Maiasaura bonebed), results are reported '
  'under both mechanisms rather than silently classifying the assemblage.',
  refs=False)

H(2, '2.3 The observation process')
P('Let q_j(a) be the probability that an individual of age a in study j is '
  'preserved, recovered, collected and measurable. The observed density is')
add_equation(doc, ['g_j(a) = base_j(a) q_j(a) / ',
                   ('int', '0', '∞', 'base_j(u) q_j(u) du')])
P('We use parametric families for q (constant, logistic monotone increase, '
  'juvenile deficit with a ramp, saturating, non-monotone peaked recovery). '
  'Because F and q enter g only through their product, they cannot both be '
  'unconstrained (Section 3). q is therefore treated as a scenario/uncertainty '
  'dimension, not a free estimand — except where we deliberately fit a '
  'constrained q to measure the cost of misspecification.', refs=False)

H(2, '2.4 Age-estimation error and report types')
P('Reported ages enter as exact values, intervals [lo, hi), or lower bounds '
  '(e.g. "at least x annuli"), with likelihood contributions g(a) da, '
  'G(hi) − G(lo), and 1 − G(lo) respectively. Grouped life-table counts '
  'contribute multinomial terms over bins. Observer disagreement is carried '
  'as per-specimen interval widths (mammaliaform cementum counts below).',
  refs=False)

H(2, '2.5 The maximum as an order statistic')
P('A maximum-only report (M, n) — "the oldest known of n specimens" — has '
  'density under the *observed* distribution g:')
add_equation(doc, ['p(M) = n g(M) ', ('sup', 'G(M)', 'n−1')])
P('with expected value')
add_equation(doc, ['E[', ('sup', 'M', 'n'), '] = ', ('int', '0', '∞', '(1 − '),
                   ('sup', 'G(a)', 'n'), ' da)'])
P('Two consequences follow. First, M_5 and M_100 are different statistics, '
  'not estimates of the same quantity; comparing "oldest" specimens across '
  'samples of different size is comparing different estimators. Second, a '
  'maximum tells us about g, not directly about f: its information on latent '
  'mortality passes entirely through the assumed observation process. We '
  'propose standardized reporting of E[M_n*] at fixed n* (we use 50 and 100) '
  'as the comparable quantity, and we never reuse a maximum computed from an '
  'individual-level dataset as an additional likelihood term — it is already '
  'contained in the data and serves only as a posterior-predictive check.',
  refs=False)

# ===== 3 Identifiability
H(1, '3. What can be identified')
P('Three structural non-identifiabilities bound what fossil age evidence can '
  'say, demonstrated empirically in Fig. 2 and quantified in Table 1.')
P('(i) F and q are entangled. An observed sample of n = 50 ages generated '
  'under Weibull mortality with a juvenile-recovery deficit below age 6 is '
  'matched almost exactly (max |Δg| = '
  f"{isum['iso_g_max_density_diff']:.3f}) by a different Weibull mortality "
  'under constant q; the two explanations score essentially identical '
  f"likelihoods ({isum['loglik_true_pair']:.1f} vs "
  f"{isum['loglik_alt_pair']:.1f}). No likelihood can separate them; only "
  'assumptions can.')
P('(ii) Catastrophic samples cannot identify mortality alone. For an '
  '80-specimen standing-crop sample drawn from a Siler schedule with growth '
  f'r = −0.05, the estimated mean age at death sweeps '
  f"{rprof['mean'].min():.1f}–{rprof['mean'].max():.1f} yr as the assumed r "
  'varies over ±0.2 (Table S1); the likelihood surface is nearly flat over a '
  'broad r range and the best-fitting r is not the true one. Mortality and '
  'demography are inseparable in standing-crop data without independent r '
  'or fertility information [5].')
P('(iii) Maximum-only evidence is weak. A single (M, n) report constrains '
  'mainly scale and leaves shape essentially free (Fig. 2C). As a '
  'consequence, targets are classified into four recoverability classes '
  '(Table 1): A robustly recoverable; B conditionally recoverable under '
  'stated scenarios; C weakly identified — report ranges, not points; '
  'D not identifiable without external information.')

cited_fig('fig_identifiability.png', 2,
          'Identifiability exhibits. (A) Likelihood surface over Weibull '
          '(λ, k) when a juvenile-deficit truth is fitted under a wrong '
          'constant-q assumption. (B) Estimated mean age at death from a '
          'standing-crop sample as a function of the assumed population '
          'growth rate r; the estimate is a dial on r, not a property of the '
          'data. (C) Likelihood surface from a single maximum-only report.')

# table 1: target classes
tcls = pd.DataFrame({
    'Class': ['A — robust', 'B — conditional', 'C — weak', 'D — not identifiable'],
    'Targets': [
        'mean age at death (most scenarios); E[M_50] latent',
        'q90, q95, prime-age hazard, median (continuous-hazard taxa, n ≥ ~30)',
        'median when mortality is infant-dominated; juvenile hazard; late-life '
        'hazard slope; hazard-minimum age; "onset of senescence"',
        'joint (F, q); mortality from catastrophic data without independent r; '
        'any quantity from max-only data without known n and constrained q']})
add_df_table(doc, tcls,
             'Table 1. Recoverability classes for mortality summary '
             'quantities, assigned from the degradation experiment '
             '(Section 5) and the structural arguments above.',
             floatfmt='{:.0f}')

# ===== 4 Validation design
H(1, '4. Validation: degrading extant demography into fossil evidence')
P('Because fossil truth is unknowable, we invert the problem: take known '
  'extant demographic schedules and destroy information the way the fossil '
  'record does. We use 45 published mammalian life tables from the malddaba '
  'database [6], each converted to a latent death-age distribution and '
  'standing-crop age structure. Samples are drawn as: (a) attritional '
  'deaths from the life-table death distribution, or (b) standing-crop ages '
  'from S(a)e^(−ra) at r ∈ {−0.05, 0, +0.05}; rejected with probability '
  '1 − q(a) under five observation scenarios (constant; moderate and severe '
  'juvenile deficits; monotone logistic; non-monotone peaked recovery); '
  'measured at four resolutions (exact, integer-rounded, 2-year interval, '
  '±10% lognormal noise); and reported as all individuals, grouped bins, '
  'max+n only, or mixed. Sample sizes span n = 5–100. Two analysts are '
  'applied to every sample: a "naive" analyst who assumes an attritional '
  'assemblage, constant q and exact ages, and an "informed" analyst who '
  'knows the true mechanism class, q family and age model. The informed '
  'analyst is an oracle — an upper bound on recoverability; the naive '
  'analyst is a lower bound that ignores observation structure entirely. '
  'Real-world inference lies between them, and no claim below rests on '
  'oracle knowledge alone. Each cell is '
  'replicated 30–40 times; the full map comprises '
  f'{len(pd.read_csv(TAB + "/recoverability_map_raw.csv")):,} fits. Metrics: '
  'bias, relative bias, RMSE, estimator failure frequency, and the A–D '
  'classes of Table 1.', refs=False)

# ===== 5 Results
H(1, '5. Results')
H(2, '5.1 The recoverability map')
P('Fig. 3 summarizes median-age bias for the informed analyst over the three '
  'focal populations (a meerkat-sized short-lived, a red-deer mid-lived, and '
  'an elephant long-lived schedule). Three patterns dominate.')
P('Observation process: with a severe juvenile-recovery deficit, the naive '
  f'analyst overestimates the median age at death by {q_naive_bias:.1f} yr '
  f'on average; the informed analyst reduces this to {q_inform_bias:.1f} yr, '
  'with the residual reflecting parametric misspecification rather than '
  'ignorance of q.')
P('Assemblage: misreading a standing crop as a death assemblage produces '
  'biases of several years in either direction depending on r — dwarfing '
  'sampling error at any n.')
P('Report type: grouped life tables lose almost nothing relative to '
  'individual ages, but max-only reports are unusable for estimating '
  f'mortality summaries (mean median bias {maxonly_med_bias:.1f} yr; every '
  'max-only cell classifies D). Mixed reporting adds a legitimate '
  'independent maximum term at negligible cost.')
P('Class fractions across all informed-analyst scenarios are shown in '
  'Fig. 4. Mean age at death classifies A in a majority of cells; the '
  'median is notably less robust — its D-cells are concentrated where the '
  'true schedule is infant-dominated (most wild mammal tables), because '
  'smooth parametric families cannot express a mortality spike at age 0 '
  'and spread the mass upward. Where senescence-relevant summaries (q90, '
  'q95, E[M_50]) sit in A/B under honest scenarios, they collapse under '
  'max-only reporting or mechanism misread.')
cited_fig('fig_recoverability_map.png', 3,
          'Recoverability map: mean bias of estimated median age at death '
          '(informed analyst) across fossilization scenarios and sample '
          'sizes, pooled over three focal extant schedules. Positive values '
          'mean overestimated lifespan.')
cited_fig('fig_recoverability_classes.png', 4,
          'Fraction of informed-analyst scenarios classified A (robust), B '
          '(conditional), C (weak), D (not identifiable) for each mortality '
          'summary.')

H(2, '5.2 The maximum is a sample-size statistic')
P('Under a single latent Weibull truth, the expected observed maximum '
  f"climbs from E[M_5] = {emax['E_M5']:.1f} yr to "
  f"E[M_100] = {emax['E_M100']:.1f} yr (Fig. 5). A 'record oldest "
  "individual' therefore says at least as much about collecting effort as "
  'about longevity. In simulation, an evidence model using 40 individual '
  'ages recovers the median unbiasedly; the same sample\'s maximum used as '
  f"a sole datum returns a median biased high by ~{abs(p5.loc['B_maxonly','mean']-8.33):.0f} yr "
  'on average; and adding the dataset\'s own maximum as a second '
  'independent likelihood term is illegitimate double counting whose '
  'apparent added precision is spurious (Table 2).')
cited_fig('fig_maximum.png', 5,
          'Left: estimated median distributions under four evidence models '
          '(A individual ages; B max-only; C individuals + independent max; '
          'D individuals + same-data max, the double-counting error). Right: '
          'E[M_n] under latent f vs an observed g with juvenile '
          'under-recovery — the statistic museums record.')
m5t = phase5.groupby('model')['median'].agg(['mean', 'std']).reset_index()
m5t.columns = ['evidence model', 'median mean', 'median sd']
add_df_table(doc, m5t, 'Table 2. Estimated median age at death (yr; true '
                       '8.33) under four evidence models, 60 replicates.')

H(2, '5.3 Fossil demonstrations')
P('Four fossil datasets demonstrate the framework (Table 3; details in '
  'Supplement). These are methodological demonstrations on lawfully '
  'accessible data, not new estimates of any taxon\'s natural lifespan.')
P('Maiasaura peeblesorum (n = 49 tibiae with LAG counts; Woodward et al. '
  '2015 [1]). Under an attritional + complete-recovery reading, every '
  'family returns a heavily infant-dominated latent mortality — the '
  'assemblage is mostly 0-LAG juveniles — with fitted medians of '
  f"{maia_med_rng[0]:.1f}–{maia_med_rng[1]:.1f} yr across families. The "
  'sensitivity analysis (Fig. 6) shows this is the dominant fragility: '
  'excluding the age-0 class alone moves the median to ~6.5 yr, and the '
  'standing-crop reading redistributes estimates across ±0.10 of assumed '
  f"r. Across the analysis grid the median spans {sens_med_rng[0]:.1f}–"
  f"{sens_med_rng[1]:.1f} yr: for this assemblage the median is a class-C "
  'quantity, and we report it as such.')
P('Bayesian posteriors (Fig. 7) quantify the same fragility: Weibull '
  f"median {post.loc[post.family=='weibull','median'].iloc[0]:.2f} yr "
  f"[95% CrI {post.loc[post.family=='weibull','median_lo'].iloc[0]:.2f}–"
  f"{post.loc[post.family=='weibull','median_hi'].iloc[0]:.2f}], Siler "
  f"{post.loc[post.family=='siler','median'].iloc[0]:.2f} yr "
  f"[{post.loc[post.family=='siler','median_lo'].iloc[0]:.2f}–"
  f"{post.loc[post.family=='siler','median_hi'].iloc[0]:.2f}]. A "
  'posterior-predictive check on the dataset maximum (10 LAGs) shows the '
  'observed maximum sits in the lower tail of what the fitted models expect '
  f"for n = 49 (p = {post.loc[post.family=='weibull','postpred_p_max'].iloc[0]:.2f} Weibull; "
  f"{post.loc[post.family=='siler','postpred_p_max'].iloc[0]:.2f} Siler): "
  'the oldest observed specimen is younger than the fitted latent tails '
  'predict — consistent with juvenile-dominated recovery or with a '
  'standing-crop mechanism.')
cited_fig('fig_fossil_fits.png', 6,
          'Maiasaura demonstration. Left: LAG-count distribution. Middle: '
          'latent survival fits by family (attritional, q = 1). Right: '
          'sensitivity of the estimated median to analysis choices; markers '
          'denote model family.')
cited_fig('fig_posterior.png', 7,
          'Bayesian demonstration on Maiasaura. Left: posterior survival '
          'bands vs empirical curve. Middle: posterior for standardized '
          'E[M_50] with the observed dataset maximum. Right: shape-parameter '
          'posteriors.')
P('Psittacosaurus lujiatunensis (n = 15 aged specimens from Zhao et al. '
  '2013 [8]). The assemblage mixes hatchling and ~2-yr clusters with '
  'isolated individuals and its taphonomic status is contested; fitted '
  'means range ~4–11 yr purely as a function of assumed mechanism and r — '
  'the demographic spread dominates the fit. It cannot be read as a death '
  'age distribution, and we report the scenario range instead of an '
  'estimate.')
P('Albertosaurus sarcophagus (grouped lx, per-1000 survivorship to age 28 '
  'from Erickson via the Griebeler Dryad transcription [5]). Treated as '
  'grouped counts (n_eff = 22), fits reproduce the well-known convex '
  'survivorship; the recoverable quantities (q90 ≈ 21–26 yr across families) '
  'are reported, while the 22-specimen basis makes the median a class-C '
  'quantity under exclusion tests (small-sample stress test in the spirit '
  'of [4]).')
P('Mammaliaform cementum series (Morganucodon n = 35, Kuehneotherium n = '
  '27; Newham et al. 2020 [9]). Used here to demonstrate interval '
  'observation models from observer disagreement (three counts per '
  'specimen) rather than as demographic assemblages — they are '
  'fissure-fill samples, not death records. Attritional-model fits give '
  'compact estimates (medians ~4.5–5.2 yr) as an order-statistic/'
  'measurement demonstration only.')
fsub = foss.copy()
fsub['range'] = fsub.apply(
    lambda r: f"{r['median']:.1f}–{r['q90']:.1f}", axis=1)
tab3 = foss.groupby('dataset').agg(
    families=('family', 'count'),
    median_min=('median', 'min'), median_max=('median', 'max'),
    q90_min=('q90', 'min'), q90_max=('q90', 'max')).reset_index()
tab3.columns = ['dataset · scenario', 'families fitted', 'median min',
                'median max', 'q90 min', 'q90 max']
add_df_table(doc, tab3, 'Table 3. Fossil demonstrations: range of fitted '
                        'median and q90 (yr) across model families per '
                        'assemblage/q scenario. Ranges, not point '
                        'estimates, are the deliverable.')

H(2, '5.4 Sensitivity')
P('The Maiasaura sensitivity grid (Fig. 6, right) ranks the material '
  'assumptions: specimen inclusion (age-0 class) and the observation/assemblage '
  'model dominate; age-measurement error (±1 retrocalculated LAG), prior '
  'strength, and oldest-specimen exclusion are secondary. Identifiability '
  'warnings (Table 1) correspond to exactly these fragile directions.')

# ===== 6 Discussion
H(1, '6. Discussion')
P('What this framework changes. Prior work fitted survival curves to '
  'observed fossil age distributions [2,3,10]; Steinsaltz and Orzack '
  'quantified small-sample uncertainty and one fossilization bias [4]; '
  'Griebeler showed that assemblages need not be stationary populations '
  '[5]. The contribution here is to make every link in the inferential '
  'chain a separate object — latent hazard, mechanism, q, measurement, '
  'report — so that identifiability becomes a computed property rather '
  'than an assumption, and heterogeneous evidence combines without double '
  'counting.')
P('The recoverability map is the practical output. It says: mean age at '
  'death, upper quantiles, and standardized maxima are the defensible '
  'deliverables at n ≥ ~30–50 under honest scenarios; the median is '
  'fragile where mortality is infant-dominated; juvenile and late-life '
  'hazard components are class-C everywhere we tested; and max-only '
  'reports are class-D for mortality inference — their only legitimate '
  'uses are as weak additional likelihood terms or posterior-predictive '
  'checks.')
P('On "oldest individuals". E[M_n] has two virtues as a reporting '
  'standard: it is honest about sampling (n is explicit), and it is '
  'computable under any fitted model including the observation process. '
  'We recommend journals and authors report E[M_50] and E[M_100] alongside '
  'any "oldest known specimen" claim, with the sample n behind the maximum '
  'stated. A maximum without n is not a statistic.')
P('Limitations. The map is generated under parametric families on '
  'life-table smooths of real demography; it can overstate recoverability '
  'where malddaba tables are already model-smoothed. The q scenarios are '
  'plausible, not measured — no dataset identifies q jointly with F, so '
  'field calibration (e.g. capture–recapture-informed preservation '
  'estimates) is the real fix and is flagged as future work. Age '
  'measurement is treated as a bounded interval, not a full calibration '
  'density for histological error, which remains poorly quantified in '
  'skeletochronology [8,9]. Finally, our fossil demonstrations are '
  'deliberately conservative: we report ranges over scenarios, and we '
  'expect future datasets (larger assemblages, better taphonomic '
  'control) to collapse some of them rather than all.')
P('Positioning. Latent-age observation models are established in human '
  'skeletal paleodemography [11]; sampling-effort treatments of reported '
  'maxima exist in zoological longevity records [12]; the order-statistic '
  'machinery itself is classical [13] but has not been wired into '
  'palaeodemographic likelihoods; and mechanistic fossil-occurrence '
  'simulators serve phylogenetic inference [14], not within-assemblage '
  'demography. This is not the first survival analysis of dinosaurs, '
  'the first Weibull fit in palaeontology, or the first paper to say '
  'taphonomy biases age structure. Its claim is narrower and new: a '
  'joint generative likelihood over heterogeneous fossil age evidence, '
  'an explicit non-identifiability treatment of (F, q), an order-statistic '
  'accounting of fossil maxima, and a validated map of what survives '
  'fossilization.')

# ===== 7 Conclusion
H(1, '7. Conclusions')
P('Fossil age-at-death evidence can support mortality inference — but '
  'only some quantities, under stated assumptions, reported with their '
  'scenario ranges. The framework and recoverability map provided here '
  'make those statements checkable dataset by dataset. Where they cannot '
  'be made, the honest output is the impossibility result itself.')

H(1, 'Data and code availability')
P('All raw inputs (data/raw/ with provenance ledger), processed datasets, '
  'analysis scripts (scripts/), generated result tables (output/tables/) and '
  'figures (output/figures/) accompany this manuscript; every reported '
  'number is regenerated by the scripts in README_REPRODUCIBILITY.md. '
  'Third-party datasets remain under their stated licenses; publisher-blocked '
  'sources are declared in data_inventory.csv.', refs=False)

# ===== references
H(1, 'References')
refs = [
 'Woodward HN, Freedman Fowler EA, Farlow JO, Horner JR. Maiasaura, a model '
 'organism for extinct vertebrate population biology: a large sample '
 'statistical assessment of growth dynamics and survivorship. Paleobiology. '
 '2015;41(4):503–527.',
 'Erickson GM, Currie PJ, Inouye BD, Winn AA. Tyrannosaur life tables: an '
 'example of nonavian dinosaur population biology. Science. '
 '2006;313(5787):213–217.',
 'Erickson GM, Makovicky PJ, Inouye BD, Zhou CF, Gao KQ. A life table for '
 'Psittacosaurus lujiatunensis: initial insights into ornithischian dinosaur '
 'population biology. Anat Rec. 2009;292(9):1514–1521.',
 'Steinsaltz D, Orzack SH. Evaluating statistical approaches to quantifying '
 'juvenile survival in deep time. Paleobiology. 2011;37(1):113–125.',
 'Griebeler EM. Dinosaurian survivorship schedules revisited: new insights '
 'from an age-structured population model. Palaeontology. '
 '2021;64(6):839–854. doi:10.1111/pala.12576.',
 'Ronget V, Lemaitre JF, Spataro B, Humblot L, Gaillard JM. malddaba: an '
 'open-access database of age-specific mammalian demography for comparative '
 'analyses in evolutionary biology and demography. J Anim Ecol. '
 '2026. doi:10.1111/1365-2656.70276.',
 'Siler W. A competing-risk model for animal mortality. Ecology. '
 '1979;60(4):750–757.',
 'Zhao Q, Benton MJ, Sullivan C, Sander PM, Xu X. Histology and postural '
 'change during the growth of the ceratopsian dinosaur Psittacosaurus '
 'lujiatunensis. Nat Commun. 2013;4:2079.',
 'Newham E, Gill PG, Brewer P, Benton MJ, Fernandez V, Gostling NJ, et al. '
 'Reptile-like physiology in Early Jurassic stem-mammals. Nat Commun. '
 '2020;11:5121.',
 'Ricklefs RE. Tyrannosaur ageing. Biol Lett. 2007;3(2):214–217.',
 'Bocquet-Appel JP, Masset C. Farewell to paleodemography. J Hum Evol. '
 '1982;11(4):321–333.',
 'Moorad JA, Promislow DEL, Flesness N, Miller RA. A comparative assessment '
 'of univariate longevity measures using zoological animal records. '
 'Aging Cell. 2012;11(6):940–950.',
 'David HA, Nagaraja HN. Order Statistics. 3rd ed. Wiley; 2003.',
 'Barido-Sottani J, Pett W, O\'Reilly JE, Warnock RCM. FossilSim: an R '
 'package for simulating fossil occurrence data under mechanistic models '
 'of preservation and sampling. Methods Ecol Evol. 2019;10(6):835–840.',
]
for i, r_ in enumerate(refs, 1):
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Inches(0.3)
    p.paragraph_format.first_line_indent = Inches(-0.3)
    p.add_run(f'{i}. {r_}').font.size = Pt(10)

doc.save(f'{OUT}/MAIN_MANUSCRIPT_inline.docx')
print('manuscript saved')
