# 03 — Literature positioning (Phase 8)

## What we claim — and what we do not

This paper is a **methods and recoverability** contribution. Its claim is
architectural and diagnostic, not a new empirical estimate of any extinct
taxon's lifespan.

### Positioning against each literature line

- **Erickson et al. (2004–2009) & Woodward et al. (2015).** Pioneered
  histologically aged dinosaur assemblages and static life tables. They report
  observed age structure; we add an explicit generative chain
  (latent μ(a) → assemblage mechanism → q(a) → age-measurement → report type)
  and ask what it can and cannot identify. We use their data (Maiasaura) as a
  demonstration, not as a target for a better point estimate.

- **Steinsaltz & Orzack (2011).** Closest predecessor on uncertainty: CIs on
  age-specific survival, power analysis, one size-dependent-fossilization
  worked example. We differ in four ways: parametric latent hazard families;
  explicit q(a) scenario grids rather than a single illustrative correction;
  order-statistic treatment of maxima; and a systematic recoverability map
  validated on degraded extant schedules rather than power calculations alone.
  Their small-sample caveat is confirmed and quantified, not contradicted.

- **Griebeler (2021).** Established that bone assemblages need not be
  stationary-age-distribution populations and corrected survivorship via
  fecundity + λ. We treat the same mechanism distinction but from the
  likelihood side: assemblage mechanism and growth rate r are handled as
  explicit model scenarios, and we quantify the resulting estimate ranges
  rather than requiring a stationarity correction.

- **Ricklefs (2007) and parametric survivorship fitting.** Weibull/Gompertz
  fits to observed curves exist; we fit the *latent* hazard under candidate
  observation processes and demonstrate the bias when the observed curve is
  fit directly.

- **Human skeletal paleodemography** (Bocquet-Appel & Masset; Konigsberg &
  Frankenberg; Buckley/Holzapfel). Latent-age observation models are
  established there for age indicators; our framework is the non-human-fossil
  analogue but adds order-statistic maxima and extant-degradation validation,
  which that literature does not use.

- **Maximum-longevity literature** (Møller; Xia & Møller; Moorad et al.;
  Beukema & Meehan). Sampling-effort regressions on reported maxima exist in
  ornithology and fisheries. We instead derive the maximum's likelihood under
  the *observed* CDF and propose standardized E[M_n*] — a model-based
  standardization, not a regression correction.

### Non-claims (guardrail check)
We do not claim to be first to: fit survivorship to dinosaurs, use Weibull or
life tables in paleodemography, discuss taphonomic bias, or note that max
lifespan depends on sampling. All novel claims are limited to the four items
in the novelty statement (01_novelty_audit.md).

## Empirical stance
Fossil-case outputs are reported as **ranges and recoverability classes, not
as definitive paleobiological estimates**. Where the data cannot support a
claim (e.g. Maiasaura median under juvenile-exclusion sensitivity), the
inability is the reported result.
