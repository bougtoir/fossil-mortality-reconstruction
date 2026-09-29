# TERMINOLOGY_AUDIT (finishing pass)

Searched: manuscript, abstract, captions, supplement, cover letter, table
contents for lifespan/life expectancy/longevity/maximum/oldest/
survivorship/senescence families.

## Rules applied (per finishing prompt)
- Observed maxima → "observed maximum" / "observed maximum age".
- Model-based maxima → E[M_n] / "standardized expected maximum".
- "Maximum lifespan" never used as synonym for observed maximum.
- Means → "mean age at death" (not "life expectancy").
- "Senescence" not inferred from hazard shape alone.

## Changes made in Paleobiology build
| Where | Before | After |
|---|---|---|
| Intro ¶4 | "The mean lifespan of this taxon cannot be recovered" | "The mean age at death of this taxon cannot be recovered" |
| Fig. 3 caption | "overestimated lifespan" | "overestimation of the median" |
| §The maximum | "says … about longevity" | "says … about the underlying mortality schedule" |
| §Fossil demos | "not new estimates of any taxon's natural lifespan" | "not new estimates of any taxon's mortality schedule or longevity" (taxonomy phrasing, not a species-limit claim) |
| Results ¶5 | "senescence-relevant summaries" | "late-life summaries" |
| Table 1 class C | '"onset of senescence"' | dropped; "hazard-minimum age" retained |
| Limitations | — | added explicit "E[M_n*] is a model-based comparative statistic, not a biological maximum lifespan" |

## Deliberately retained
- '"the lifespan" of a species' in intro — quoted as the misleading usage
  being criticized.
- '"oldest known" individual/specimen' — the object under study.
- "survivorship" only when discussing fitted survival functions S(a) or
  published life-table work (correct usage); observed fossil age-frequency
  distributions are called "observed age distribution"/"LAG-count
  distribution", never "survivorship of the fossil sample".
- Abstract phrase required by prompt applied verbatim: "Mean age at death
  and sample-size-standardized expected maxima E[M_n] were among the more
  recoverable summaries under …".
