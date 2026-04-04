# upstream-community

Reference ML implementations for Upstream's healthcare denial prediction methodology.

**What this is**: Open-source reference code demonstrating the statistical and ML techniques behind Upstream's Revenue Intelligence Platform. Uses only public CMS data — no production model weights, no proprietary payer data, no PHI.

**What this is not**: Production code. The production system has 40+ features, live payer behavioral graphs, and real-time 835 ingestion. This repo illustrates the methodology so the broader RCM community can learn from and build on it.

---

## What's Here

### `reference/` — 7 modules

| Module | What it does |
|--------|-------------|
| `carc_rarc_utils.py` | Parse and categorize CMS CARC denial codes. Plain-English descriptions, corrective actions, and regulatory basis for each code. |
| `denial_prediction_reference.py` | CatBoost denial predictor with temporal cross-validation and SHAP explainability. 15-feature reference (production uses 40+). |
| `drift_detection_reference.py` | Chi-square + KS tests to detect when a payer changes their denial behavior. The statistical core of Upstream's DriftWatch early-warning engine. |
| `denial_clustering.py` | K-means payer clustering into behavioral archetypes: Aggressive Denier, Slow Payer, Prompt Payer, Underpayer. Seed for the "31 practices" network signal. |
| `dental_denial_clustering.py` | Dental-specific denial clustering using CDT code patterns. ADA claim data compatible. |
| `aba_auth_predictor.py` | GBM model predicting ABA prior auth approval probability from insurance attributes and diagnosis codes. |
| `payer_behavior_detector.py` | Composite payer behavioral fingerprinting using denial rate trends, payment velocity, and adjudication pattern changes. Powers `check_payer_behavior` in the MCP. |

### `notebooks/` — Jupyter walkthroughs

| Notebook | What it teaches |
|---------|----------------|
| `01_payer_clustering_walkthrough.ipynb` | End-to-end: load CMS data, engineer features, run K-means clustering, visualize payer archetypes. Uses `denial_clustering.py`. |
| `02_patient_propensity_tutorial.ipynb` | End-to-end: build a GBM collectibility scorer from public claim attributes, with SHAP explainability. Uses patterns from `aba_auth_predictor.py`. |

### `data/`

No data is committed. See `data/README.md` for public CMS datasets to download.

`sample_claims_schema.py` generates a 500-row synthetic CSV for local testing.

---

## Methodology vs Production

| Aspect | This repo | Production |
|--------|-----------|------------|
| Features | 15 public-derivable features | 40+ including payer behavioral graph, auth policy changes |
| Training data | CMS SynPUF (synthetic) | Live 835 remittance data |
| Model weights | Not included | Private |
| Drift detection | 3 statistical tests | 12+ tests with payer-specific thresholds |
| Clustering | Basic K-means, 5 features | Deep behavioral fingerprinting, 200+ practices, real-time |
| Retraining | Manual | Automated weekly with data drift triggers |

---

## Install

```bash
pip install -r requirements.txt
```

Python 3.10+ recommended.

---

## Quick Start

### CARC code lookup

```python
from reference.carc_rarc_utils import parse_carc, group_by_category

# Look up a single code
info = parse_carc("97")
print(info.description)
# "The benefit for this service is included in the payment/allowance
#  for another service/procedure that has already been adjudicated."
print(info.corrective_action)
# "Review NCCI edits for the code pair. Add modifier -59 or -X{EPSU}..."

# Also handles prefixed codes from 835 files
info = parse_carc("CO-97")   # same result

# Analyze a batch of denials
codes = ["97", "50", "97", "16", "97", "197"]
by_category = group_by_category(codes)
# {"bundled": [...], "non_covered": [...], "claim_information_missing": [...], "authorization": [...]}
```

### Payer clustering

```python
import pandas as pd
from reference.denial_clustering import cluster_payers, label_clusters

df = pd.read_csv("data/sample_claims.csv")
payer_profiles = cluster_payers(df, n_clusters=4)
labeled = label_clusters(payer_profiles)
# Returns DataFrame with cluster labels:
# "Aggressive Denier", "Slow Payer", "Prompt Payer", "Underpayer"
```

### Denial prediction (requires SynPUF or your own 835 data)

```python
import pandas as pd
from reference.denial_prediction_reference import build_features, train, explain

df = pd.read_csv("data/sample_claims.csv")
X = build_features(df)
y = df["is_denied"]

model, metrics = train(X, y)
print(f"CV AUC: {metrics['cv_auc_mean']:.4f} +/- {metrics['cv_auc_std']:.4f}")

importance = explain(model, X.head(500))
print(importance.head(5))
```

### Payer drift detection

```python
import pandas as pd
from reference.drift_detection_reference import detect_drift

baseline = pd.read_csv("data/aetna_90day_baseline.csv")
current = pd.read_csv("data/aetna_last_7days.csv")

report = detect_drift("Aetna", baseline, current)
if report.drift_detected:
    for alert in report.alerts:
        print(f"{alert.feature}: {alert.baseline_rate:.1%} -> {alert.current_rate:.1%} (p={alert.p_value:.4f})")
```

### ABA prior auth prediction

```python
import pandas as pd
from reference.aba_auth_predictor import predict_approval

auth_request = {
    "payer": "unitedhealthcare",
    "diagnosis_primary": "F84.0",
    "cpt_codes": ["97153", "97155"],
    "requested_hours_weekly": 20,
    "patient_age": 7,
}

result = predict_approval(auth_request)
print(f"Approval probability: {result.probability:.1%}")
print(f"Top risk factors: {result.risk_factors}")
```

---

## Using with CMS SynPUF Data

1. Download the 1% SynPUF sample from the [CMS website](https://www.cms.gov/data-research/statistics-trends-and-reports/medicare-claims-synthetic-public-use-files) (~460MB)
2. Map the SynPUF columns to the schema in `sample_claims_schema.py`
3. Run `notebooks/01_payer_clustering_walkthrough.ipynb`

See `data/README.md` for all supported public datasets.

---

## Related

- [upstream.cx](https://upstream.cx) — Revenue Intelligence Platform
- [upstream-mcp](https://github.com/upstream-cx/upstream-mcp) — MCP server: bring Upstream intelligence into Claude
- [upstream.cx/developers](https://upstream.cx/developers) — API docs

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

Issues and PRs welcome. Scope:
- Additional CARC/RARC codes in `carc_rarc_utils.py`
- Improved feature engineering in `denial_prediction_reference.py`
- Notebooks demonstrating the reference implementations on public data
- Bug fixes and documentation improvements

Out of scope: anything requiring proprietary payer data or production Upstream internals.

---

## License

MIT. See LICENSE.

Upstream's production model weights and proprietary payer behavioral data remain private.
