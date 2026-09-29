# Data and code repository bundle — "Beyond the oldest known individual"

Repository-ready bundle for deposit in Dryad/Zenodo on acceptance
(Paleobiology covers deposit costs). Not yet deposited — do not cite a
repository DOI until deposition is actually completed.

## Contents
- `scripts/` — every script used for the results in the manuscript:
  generative model + likelihood (`mortality_models.py`, `fitting.py`),
  degradation pipeline (`degrade.py`), experiments
  (`phase3_identifiability.py`, `phase4_experiments.py`,
  `phase4_classify.py`, `phase5_maximum.py`, `phase6_fossil.py`,
  `phase6b_bayes.py`, `phase7_sensitivity.py`), figure/document
  generators (`make_figures.py`, `make_manuscript*.py`,
  `make_supplement_paleobiology.py`, `make_cover_paleobiology.py`,
  `docx_utils.py`), Dryad fetcher (`dryad_fetch.py`).
- `data_clean/` — processed datasets used by the analyses.
- `result_tables/` — all result CSVs/JSONs the manuscript numbers are
  generated from (recoverability_map.csv + raw, phase5/6/6b/7 tables,
  identifiability tables).
- `data_inventory.csv` — machine-readable source ledger (URL, licence,
  access status); `data/raw` is retained locally per provenance policy
  but third-party raw files are redistributed only where their licence
  permits — see ledger.

## Reproduction
See `README_REPRODUCIBILITY.md` for the ordered pipeline. Python 3.10;
numpy, pandas, scipy, matplotlib, emcee, arviz, python-docx, python-pptx.
All random draws use deterministic per-cell seeds (crc32-based), so
result tables regenerate identically.

## Suggested citation text (draft)
Onishi T. Data and code for: "Beyond the oldest known individual:
reconstructing mortality distributions from fossil age-at-death
evidence." [Repository DOI to be inserted after Dryad/Zenodo deposit.]
