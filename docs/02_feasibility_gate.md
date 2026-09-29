# 02 — Feasibility Gate

## GO/NO-GO criteria assessment

| Criterion | Status | Evidence |
|---|---|---|
| ≥2 usable fossil datasets with individual or grouped age info | **MET** | Maiasaura (n=50 individual LAG counts, Dryad); Newham Morganucodon (n=35) + Kuehneotherium (n=27) individual cementum counts with 3-observer replicates; Psittacosaurus Zhao 2013 (n=16 specimen ages + cluster structure); Albertosaurus grouped lx (n=22, via Griebeler Dryad README) |
| ≥1 fossil dataset with enough observations for meaningful demonstration | **MET** | Maiasaura n=50 (largest published histological sample for an extinct taxon) |
| ≥1 high-quality extant age-specific demographic dataset for validation | **MET** | malddaba: 45 population life tables (lx, mx, ex) covering primates, ungulates, rodents, pinnipeds, cetaceans — lifespan range ~5-60+ yr |
| No published paper implementing complete framework | **MET (as of 2026-09-29 audit)** | See 01_novelty_audit.md |
| Simulation shows some summaries recoverable under realistic degradation | **VERIFIED in Phase 3-4** (gate re-checked there; median/quantiles recoverable at n≥~30-50 under several scenarios; pre-registered as plausible) |

## Data accessibility outcomes

| Source | Outcome |
|---|---|
| Woodward 2015 Dryad | FULL — per-specimen LAG counts extracted (Supp. Table 1) |
| Newham 2020 supplementary | FULL — MOESM5 3-observer counts extracted (35+27) |
| Zhao 2013 ncomms3079 | FULL — Supp Tables S1-S2 ages extracted (16 specimens) |
| malddaba life tables | FULL — 45 life tables exported |
| Griebeler 2021 | PARTIAL — paper PDF via dinodata.de mirror; Dryad record contains only README.txt (R scripts referenced but not uploaded); Albertosaurus lx transcribed |
| Erickson 2009 (Psittacosaurus life table) | BLOCKED — Wiley Cloudflare; bronze OA but inaccessible; specimen Table 1 NOT obtained |
| Erickson 2006 (tyrannosaur life tables) | BLOCKED — Science paywall |
| Steinsaltz & Orzack 2011 | BLOCKED — Paleobiology paywall; methods described in secondary sources |
| COMADRE | NOT RETRIEVED — registration-gated |
| Proboscidean age profiles | NOT LOCATED as open machine-readable data |

## Consequences

- Tyrannosaur life tables enter only via Albertosaurus grouped lx (Griebeler README transcription) — used as a *sensitivity/small-sample* case, not primary.
- Psittacosaurus catastrophic demonstration uses Zhao 2013 clusters (defensible structure: two juvenile clusters + isolated specimens) — NOT Erickson's 80-specimen life table. Mixed/unknown assemblage — analyze under multiple mechanisms with sensitivity.
- No fabrication: all analyses use retrieved data only; blocked sources are declared.

## Verdict: **GO**

Proceed with individual-age datasets (Maiasaura, Morganucodon, Kuehneotherium, Psittacosaurus-Zhao), grouped data (Albertosaurus), and 45 extant reference schedules.
