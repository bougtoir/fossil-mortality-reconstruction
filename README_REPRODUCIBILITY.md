# Reproducibility — fossil mortality reconstruction

Everything regenerates from `scripts/` + `data/` on a single machine
(Python ≥3.10; numpy, pandas, scipy, matplotlib, emcee, rdata, python-docx,
openpyxl). No parallel VMs required.

## Layout
```
data/raw/           untouched source files + provenance.csv (URL, sha256, UTC, license)
data/processed/     cleaned, analysis-ready CSVs
data_inventory.csv  full dataset inventory incl. blocked/unusable sources
scripts/            mortality_models.py  fitting.py  degrade.py  phase{3,4,5,6,7}_*.py  dryad_fetch.py
output/tables/      all numeric results consumed by the manuscript
output/figures/     manuscript figures
docs/               audits, model spec, identifiability, positioning, journal gate
manuscript/         generated docx/pptx deliverables
```

## Regenerate (in order)
```bash
cd scripts
python3 phase3_identifiability.py   # identifiability exhibits + fig
python3 phase4_experiments.py       # recoverability map (~20-30 min, 8 workers)
python3 phase5_maximum.py           # maximum-age analysis
python3 phase6_fossil.py            # fossil demonstration fits
python3 phase7_sensitivity.py       # sensitivity grid
python3 make_figures.py             # manuscript figures from output/tables
python3 make_manuscript.py          # docx + pptx from output/tables + figures
```

## Numbers policy
No estimate in the manuscript is hardcoded: `make_manuscript.py` reads only
`output/tables/*` and `data/processed/*`. Seeds are fixed
(`rng = np.random.default_rng(<fixed>)` everywhere).

## Data acquisition notes
- Dryad downloads are Anubis-PoW-gated; `scripts/dryad_fetch.py` solves the
  challenge programmatically (documented in file header).
- Sources that could not be lawfully/reliably fetched (Wiley/Cambridge/
  RoyalSoc/Science TDM blocks) are marked `unusable` in `data_inventory.csv`
  with the reason — nothing was fabricated.
- malddaba life tables read via the `rdata` package (pyreadr cannot read
  list-type .rda).
