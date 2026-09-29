# HOSTILE_REVIEW — skeptical-reviewer assessment (pre-submission)

Reviewer persona: a hard-nosed paleodemography/methods referee who has read
Steinsaltz & Orzack, Griebeler, and the dinosaur life-table literature.

## Highest priority (must address before submission)

1. **Circularity of the "informed" analyst.** The recoverability map gives the
   informed analyst the *true* q family and mechanism. Reviewer: "You proved
   recoverability under an oracle. Real analysts don't know q." — Response
   (already partially in text, must be explicit): the informed analyst is an
   upper bound on recoverability, and the naive analyst is a lower bound;
   real claims sit between. **Action**: state this framing explicitly in
   Section 4-5 (currently implicit). Consider adding a third "realistic"
   analyst that selects q by AIC — flagged as limitation, not resolved.

2. **malddaba truth smoothness.** Life tables are partly model-smoothed, so
   the "truth" we degrade is already regular — the map may *overstate*
   recoverability. **Action**: already stated in Limitations; quantify by
   marking which tables had modeled survival series (data_used column exists
   in the Rdata — a supplementary flag column in recoverability_map would
   strengthen; feasible, moderate effort).

3. **Juvenile-deficit q is the paper's own choice of adversary.** Reviewer:
   "Your single most damaging scenario (severe juvenile deficit) is
   self-authored; how do we know real q looks like that?" — Response: cite
   histological-sampling literature on juvenile under-recovery and
   size-biased sectioning (Maiasaura inventory notes exactly this); frame q
   scenarios as spanning plausible severity, not as calibrated. **Action**:
   add one sentence + cite in Section 2.3/4.

4. **Griebeler citation is incomplete** ("verify full citation" left in
   references). Desk-level sloppiness. **Action**: resolve exact citation
   before submission — currently flagged; also Ronget/malddaba citation
   marked [verify]. Neither may ship with verify tags.

## High priority

5. **Small n at fossil demos is also small for asymptotic claims.** MLE-only
   inference for fossil fits; bootstrap/posterior shown only for Maiasaura.
   **Action**: acceptable — stated; a hostile referee may still demand
   interval estimates for Table 3 ranges. Cheap fix: report nll/AIC spread
   across families per scenario in supplement.

6. **"45 life tables" but map summaries pool only 3 focal species.** Species
   sweep exists (all pops, baseline only) but is underused in the text.
   **Action**: add one sentence quantifying cross-species baseline bias so
   the map isn't read as three anecdotes.

7. **Attritional vs catastrophic for mammaliaforms.** We call them
   "not a demographic death assemblage" yet still fit attritional models —
   a referee may call this incoherent. Response is in text
   (measurement/order-statistic demonstration only) but should be one
   sentence more explicit.

## Medium priority

8. **Double-counting demonstration is weak at n=40** (D ≈ A). The
   illegitimacy is argued, not demonstrated in numbers. **Action**: either
   show a case where D visibly misfires (small n + extreme draw) or present
   the argument purely as methodological — currently honest but thin.

9. **No explicit treatment of how a referee can re-run.** README exists;
   make the Data/Code Availability statement in the manuscript name the
   files (currently only in cover letter).

10. **OMML equations are linear-form** (not stacked fractions). Acceptable,
    but fractions in μ equations render as inline — check visually before
    submission.

## Optional / won't fix

11. No attempt to estimate q jointly (deliberate — flagged as future work).
12. Psittacosaurus n=15 too small for any class-A claim — already C/D only.
13. Proboscidean assemblages absent — inventory documents the honest
    "no accessible age-profile data" outcome.

## Assessment of claim strength
The manuscript's largest claims are about *impossibility*, which is where
the evidence is strongest (structural non-identifiability + demonstrated
estimate ranges). Positive recoverability claims are bounded by the oracle
issue (item 1). Overall: defensible as a methods/recoverability paper; the
verified citations (item 4) and analyst framing (item 1) are the only
blocking items.
