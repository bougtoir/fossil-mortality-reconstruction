# Identifiability report

Evidence: `scripts/phase3_identifiability.py`; outputs in
`output/tables/identifiability_*.csv`, `identifiability_summary.json`,
`output/figures/fig_identifiability.png`.

## Structural non-identifiabilities

### (i) F and q(a) are not jointly identifiable
The observable is g ∝ base·q. For any proposed latent F there exists a q (and
conversely) that reproduces almost any g, so unrestricted (F, q) cannot be
separated by likelihood alone. Demonstrated: an attritional sample (n = 50)
generated under Weibull(λ=10, k=2) with a juvenile-recovery deficit below age 6
is matched almost exactly by Weibull(λ, k ≈ fitted) under *constant* q —
max |Δg| = 0.0119 and the two explanations score essentially the same
likelihood on the observed sample (−139.6 vs −139.5, `identifiability_summary.json`).
Any identification therefore comes from *assumptions* on q, not from data.
This is handled by treating q as a sensitivity dimension (scenario grid),
never as a jointly estimated free function.

### (ii) Catastrophic standing-crop data cannot identify mortality alone
n(a) ∝ S(a)e^{−ra}: mortality and population growth enter as a product and
share the same exponential-like shape. Empirically (Siler truth, r = −0.05,
n = 80 ages), the estimated mean age at death under a Weibull fit sweeps
**5.3 → 20.7 yr** as assumed r varies over ±0.2, while the profile likelihood
is flat within ~2 nll over roughly r ∈ [−0.07, +0.09] and the best-fit r
(+0.057) is not the true value (`identifiability_r_profile.csv`). Catastrophic
assemblages are reported only under explicit (r, stationarity) scenarios.

### (iii) Maximum-only evidence is weak
A single (M, n) report constrains mainly the *scale* of g and leaves shape
nearly unconstrained; the (λ, k) likelihood ridge from one M_5 is broad
(fig. panel C). The same observed maximum is consistent with widely different
latent mortalities, and E[M_n] depends on both F and q. Max-only data are
usable only (a) as a weak additional term when n and the observation process
are defensibly modelled, or (b) as posterior-predictive checks.

## Target classification

| Class | Meaning | Targets |
|---|---|---|
| A — robustly recoverable | small bias across plausible q scenarios & model families at n ≥ ~30, attritional | median age at death |
| B — conditionally recoverable | recoverable under stated q model / honest reporting / n ≥ ~50; otherwise biased | q90, q95, mean age at death, prime-age hazard, standardized E[M_n*] (n* = 50,100) |
| C — weakly identified | direction/magnitude unstable across scenarios; report as ranges, not point estimates | juvenile hazard (confounded with juvenile under-recovery), late-life hazard slope, age of hazard minimum, "onset of senescence" |
| D — not identifiable | no estimator exists without external information | joint (F, q); mortality from catastrophic data without independent r/fertility; lifespan from max-only data with unknown n or unknown q |

Phase 4 revises this classification empirically (`recoverability_map.csv`);
the classification column there is authoritative.
