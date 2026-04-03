# upstream-community

Reference ML implementations for Upstream's healthcare denial prediction methodology.

**What this is**: Open-source reference code demonstrating the statistical and ML techniques behind Upstream's payer intelligence platform. Uses only public CMS data — no production model weights, no proprietary payer data, no PHI.

**What this is not**: Production code. The production system has 40+ features, live payer behavioral graphs, and real-time 835 ingestion. This repo illustrates the methodology so the broader RCM community can learn from and build on it.

---

## What's Here

### `reference/`

Three standalone modules, no external dependencies on Upstream internals:

| Module | What it does |
|--------|-------------|
| `carc_rarc_utils.py` | Parse and categorize CMS CARC denial codes. Includes corrective actions and regulatory basis for each code. |
| `denial_prediction_reference.py` | CatBoost denial predictor with temporal cross-validation and SHAP explainability. 15-feature reference (production uses 40+). |
| `drift_detection_reference.py` | Chi-square + KS tests to detect when a payer changes their denial behavior. The statistical core of Upstream's DriftWatch engine. |

### `notebooks/`

Jupyter walkthroughs (planned — contributions welcome). See `notebooks/README.md`.

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

# Frequency report
from reference.carc_rarc_utils import denial_frequency_report
report = denial_frequency_report(codes)
# [("97", 3, <CARCInfo>), ("50", 1, ...), ...]
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

---

## Using with CMS SynPUF Data

1. Download the 1% SynPUF sample from the [CMS website](https://www.cms.gov/data-research/statistics-trends-and-reports/medicare-claims-synthetic-public-use-files) (~460MB)
2. Map the SynPUF columns to the schema in `sample_claims_schema.py`
3. Run `notebooks/01_denial_prediction_walkthrough.ipynb`

See `data/README.md` for all supported public datasets.

---

## Related

- [upstream.cx/developers](https://upstream.cx/developers) — Developer docs for the Upstream API
- [upstream-mcp](https://github.com/upstream-cx/upstream-mcp) — MCP server for Upstream's payer intelligence API
- [upstream-skills](https://github.com/upstream-cx/upstream-skills) — Claude Code skills for healthcare RCM workflows

---

## Contributing

Issues and PRs welcome. Scope is limited to:
- Additional CARC/RARC codes in `carc_rarc_utils.py`
- Improved feature engineering in `denial_prediction_reference.py`
- Notebooks demonstrating the reference implementations on public data
- Bug fixes

Out of scope: anything requiring proprietary payer data or production Upstream internals.

---

## License

MIT. See LICENSE.

Upstream's production model weights and proprietary payer behavioral data remain private.
