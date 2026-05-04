# Reference Implementations

Open-source reference modules for the statistical and ML methods Upstream uses in production. All modules use public CMS data only — no PHI, no proprietary payer data, no production model weights.

## Modules

| Module | What it demonstrates |
|---|---|
| `aba_auth_predictor.py` | Gradient-boosting prior auth approval prediction for ABA therapy. Temporal cross-validation. |
| `carc_rarc_utils.py` | CARC/RARC denial code registry from public CMS lists. Lookup, classification, severity scoring. |
| `denial_clustering.py` | K-means clustering of denial patterns using CARC codes. Chi-square baseline comparison for industry signal detection. |
| `denial_prediction_reference.py` | CatBoost denial prediction with temporal cross-validation and SHAP explainability. The core methodology Upstream uses in production. |
| `dental_denial_clustering.py` | CDT-code cluster detection for dental billing. Downcoding, bundling, and frequency-limit pattern detection. |
| `drift_detection_reference.py` | Payer behavioral drift detection — the core signal that Upstream's DriftWatch engine is built on. Chi-square + Kolmogorov-Smirnov tests. |
| `payer_behavior_detector.py` | Statistical detection of payer adjudication shifts. Chi-square for categorical changes (denial rate by CARC code). |

## Methodology vs. weights

These reference modules show **how** Upstream detects payer behavior changes. They do not include production model weights, payer-specific training data, or any PHI. To use the methodology with your own data, follow the notebooks in `../notebooks/` for end-to-end walkthroughs.

## Running locally

```bash
# From the repo root
pip install -r requirements.txt

# Run a single module
python -m reference.denial_prediction_reference

# Or import in a notebook
from reference.drift_detection_reference import detect_drift
```

## Contributing

Add new reference implementations that demonstrate methodology with public data. See the org-wide `CONTRIBUTING.md` and the `upstream-community` repo `CONTRIBUTING.md` for the contribution model.

PHI in any contribution will be rejected. Synthetic data only. Document your data source in any new module.
