# HOSTILE_REVIEW_PALEOBIOLOGY (final skeptical pass, 12 challenges)

1. **"Just another fossil life-table paper?"** No: no new life table is
   presented; the unit of analysis is the evidence pipeline, and the main
   output is a recoverability map validated on extant data. Explicitly
   framed in Discussion/Positioning.
2. **"Beyond Steinsaltz & Orzack?"** S&O quantified small-sample error and
   one bias via power analysis; we add the joint likelihood, q(a) as an
   explicit process, catastrophic mechanism+r, order-statistic maxima, and
   extant degradation validation. Delimited, no priority claim. Resolved.
3. **"Beyond Griebeler?"** Griebeler demonstrated non-stationarity and
   modelled survivorship; we do not model age-structured populations but
   measure what the evidence can identify. Resolved; cited (Griebeler 2021)
   in both intro and identifiability section.
4. **Maxima double-counted?** No: dataset-internal maxima are used only as
   posterior-predictive checks; only independent literature maxima enter
   likelihoods (model C); model D exists solely to demonstrate the error.
   Verified in code (loglik_max_only only for independent maxima).
5. **Catastrophic vs attritional correct everywhere?** Standing-crop data
   are never fitted as death-age samples; every catastrophic scenario
   carries its r assumption. Psittacosaurus explicitly labelled contested
   and reported as a scenario range. Resolved.
6. **q(a) identifiable?** Stated and demonstrated as *not* jointly
   identifiable with F (iso-density pair, equal likelihood). q handled as
   scenario dimension, never silently estimated. Resolved.
7. **Sample-size thresholds oversold?** Threshold language is "n ≥ ~30–50
   under honest scenarios" — conditional, and the oracle/naive bounds are
   stated explicitly so no claim rests on oracle knowledge. Resolved.
8. **Does extant validation resemble fossil observation?** Partially — the
   map measures recoverability under *modelled* information loss, which is
   the point; limitation recorded (plausible-not-measured q; malddaba
   smooths).
9. **Fossil cases overinterpreted?** All four are labelled proofs of
   concept / stress tests; Maiasaura median reported as class-C range.
   Resolved.
10. **"Lifespan"/"senescence" too strong?** Audited — fixes applied; see
    TERMINOLOGY_AUDIT.md.
11. **Paleobiology fit vs statistics journal?** Questions and demos are
    palaeontological (dinosaur assemblages, histological aging); framework
    solves a field problem. Reasonable fit; flagged for editors.
12. **Too technical for payoff?** Length ~3,400 words with 8 numbered
    equations; supplement carries likelihood derivations. Acceptable for
    Paleobiology's quantitative remit.

## Residual risks a reviewer may still raise (disclosed, not blockers)
- Informed analyst is an oracle; stated as upper bound.
- malddaba tables partly model-smoothed; map may overstate recoverability.
- Bayesian intervals shown for Maiasaura only.
- No post-hoc "realistic" analyst with AIC-selected q (future work).
