# Notebooks

Jupyter notebooks demonstrating the reference implementations end-to-end.

Planned notebooks (contributions welcome):

- `01_denial_prediction_walkthrough.ipynb` — Train the denial prediction model on CMS SynPUF data
- `02_payer_drift_detection.ipynb` — Run drift detection on a 90-day baseline vs 7-day window
- `03_carc_rarc_analysis.ipynb` — Analyze denial code distributions and corrective action patterns
- `04_carc_denial_distribution.ipynb` — Visualize CARC frequency across payers and service types

## Setup

```bash
pip install -r ../requirements.txt
jupyter notebook
```

## Data

See `../data/README.md` for data sources. Download CMS SynPUF before running notebooks.
