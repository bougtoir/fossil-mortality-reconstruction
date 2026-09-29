# Model specification — latent mortality reconstruction from fossil age evidence

## 1. Latent demographic process

Let T > 0 be the age at death of an individual drawn from the latent population.
The mortality process is specified through the hazard μ(t), with cumulative
hazard H(t) = ∫₀ᵗ μ(u) du, survival S(t) = exp(−H(t)), CDF F(t) = 1 − S(t),
and death-age density f(t) = μ(t) S(t).

Candidate families (all parameters positive):

- **Weibull.** μ(t) = (k/λ)(t/λ)^(k−1); S(t) = exp(−(t/λ)^k).
- **Gompertz–Makeham.** μ(t) = c + a·exp(b·t); H(t) = ct + (a/b)(e^{bt} − 1).
- **Siler.** μ(t) = a₁e^(−b₁t) + a₂ + a₃e^(b₃t) — juvenile decline + age-independent + senescent increase.
- **Piecewise-constant hazard** (5 bins, boundaries at quantiles of the support): flexible benchmark.

## 2. Assemblage formation

**Attritional / accumulated death assemblage.** The base age density of the
assemblage is the death-age density itself:

  d_attr(a) = f(a) = μ(a) S(a).

**Catastrophic / standing-crop assemblage.** A rapid kill samples the *living*
age structure. Under a stable population with growth rate r:

  n_cat(a) ∝ S(a) e^(−r a);

for a stationary population r = 0 and n_cat(a) ∝ S(a). The density n_cat(a)
places mass on *survivors*, not on deaths: E[T | catastrophic draw] has no
simple mortality interpretation, and mortality parameters are entangled with r.

**Unknown / mixed.** Where the mechanism is contested (e.g. bonebeds of
disputed origin), inference is reported under each mechanism rather than
assigning one silently.

## 3. Observation process

For study j, q_j(a) = P(specimen preserved, recovered, collected, measurable
| true age a). The observed density is

  g_j(a) = base_j(a) · q_j(a) / ∫ base_j(u) q_j(u) du.

Parametric families used for q (all bounded in (0,1] or monotone):

- constant: q(a) = q₀ — equivalent to no age bias (q₀ cancels in normalization);
- logistic: q(a) = q_max · σ((a − a₅₀)/s) — monotone size/age detectability;
- juvenile deficit: q(a) = q_adult for a ≥ a_full, ramped (linear or quadratic) below;
- saturating: q(a) = q_max(1 − e^(−κa)).

q is **not** freely estimated jointly with F from one small sample: F and q
enter g only through their product, so (F, q) is identifiable only up to a
manifold. q scenarios are therefore treated as *sensitivity/uncertainty
dimensions*, not as estimands — except where we explicitly fit a constrained
q to demonstrate the degree of joint recoverability.

## 4. Age-estimation error

The reported age â of a specimen is a noisy measurement of T:

- **Exact**: P(T ∈ [â, â+da]) ∝ g(â) da — used for integer LAG/cementum counts
  with rounded ages interpreted as the bin [â, â+1) in sensitivity analyses;
- **Interval**: T ∈ [lo, hi) contributes G(hi) − G(lo);
- **Lower bound** ("at least x"): contributes 1 − G(x);
- **Observer error**: per-specimen counts from k observers modelled as
  â_obs ~ true count + error; consensus/median used in the primary analysis,
  with a discrete-error convolution in sensitivity;
- **Retrocalculated LAG counts**: treated as intervals [count, count + n_eroded]
  where the number of obliterated inner LAGs is uncertain.

## 5. Aggregate reports

**Grouped counts** (life tables): counts cᵢ in bins [eᵢ, eᵢ₊₁) contribute
cᵢ · log(G(eᵢ₊₁) − G(eᵢ)).

**Maximum-only reports.** The maximum M among n specimens drawn from the
*observed* distribution g is an order statistic with density

  p_M(m) = n · g(m) · G(m)^(n−1),

and E[M_n] = ∫₀^∞ (1 − G(a)^n) da. M enters the likelihood only through g —
not the latent F — so maxima are informative about latent mortality only via
the assumed observation process. A maximum computed from an individual-level
dataset is a posterior-predictive check, never a second likelihood term
(no double counting).

## 6. Inference

Primary: maximum likelihood on the joint likelihood over studies, with
parametric-bootstrap confidence/coverage intervals. Bayesian inference
(emcee, weakly informative log-normal priors centred on plausible scales,
prior SD 2.5 on log parameters) is used for identifiability exhibits,
posterior predictive checks, and the fossil demonstrations.

## 7. Target quantities

| Quantity | Definition |
|---|---|
| median / q90 / q95 age at death | quantiles of latent F (density f) |
| mean age at death | ∫ a·f(a) da |
| juvenile hazard | mean μ over youngest 10% of support |
| prime-age hazard | mean μ over 20–60% of support |
| late-life hazard slope | d log μ / da over last 40% of support |
| age of hazard minimum | argmin μ(a) |
| E[M_50], E[M_100] | expected maxima of n draws from latent f — the *standardized* maximum |
| observed E[M_n] | expected maximum under observed g (what a museum collection max actually measures) |
