<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)"
          srcset="https://raw.githubusercontent.com/Upstream-Intelligence/.github/main/.github/assets/upstream-wordmark-dark.svg">
  <img src="https://raw.githubusercontent.com/Upstream-Intelligence/.github/main/.github/assets/upstream-wordmark-light.svg"
       alt="Upstream" width="220" />
</picture>

# upstream-community

Open-source tooling for healthcare operators who need early-warning payer behavior intelligence.

### Open ML reference implementations for healthcare denial detection.

The statistical and ML methodology behind Upstream's Care Intelligence Platform. Public CMS data only. No production model weights. No proprietary payer data. No PHI.

[![License](https://img.shields.io/github/license/Upstream-Intelligence/upstream-community?color=0454F1)](LICENSE)
[![Issues](https://img.shields.io/github/issues/Upstream-Intelligence/upstream-community?color=0454F1)](https://github.com/Upstream-Intelligence/upstream-community/issues)
[![Python](https://img.shields.io/badge/python-3.10%2B-0454F1)](https://www.python.org/)
[![upstream.cx](https://img.shields.io/badge/upstream-cx-0454F1)](https://upstream.cx)

</div>

---

## What this is

Reference code that demonstrates how Upstream detects payer behavior shifts, predicts denials, and clusters payers into behavioral archetypes. Written so the broader healthcare RCM community can learn from the methodology, validate the techniques, and contribute back.

This is the open methodology. Not the production engine.

---

## What this is not

Production code. The production system uses 40 plus features, live behavioral graphs, real time 835 ingestion, and trained model weights that stay private. This repository teaches the patterns. The platform applies them at scale across the operator network.

It applies across healthcare specialty practices as one connected system.

---

## What is here

### `reference/` modules

| Module | What it does |
|---|---|
| `carc_rarc_utils.py` | Parse and categorize CMS CARC denial codes. Plain English descriptions, corrective actions, and regulatory basis for every code. |
| `denial_prediction_reference.py` | CatBoost denial predictor with temporal cross validation and SHAP explainability. 15 features (production uses 40 plus). |
| `drift_detection_reference.py` | Chi-square plus Kolmogorov-Smirnov tests for detecting when a payer changes their denial behavior. The statistical core of Upstream's DriftWatch engine. |
| `denial_clustering.py` | K-means payer clustering into behavioral archetypes. Aggressive Denier, Slow Payer, Prompt Payer, Underpayer. |
| `dental_denial_clustering.py` | Specialty specific clustering using CDT code patterns. Compatible with ADA claim data. |
| `aba_auth_predictor.py` | Gradient boosted authorization approval predictor. ABA reference implementation. Use as a template for other specialties (dental, SNF, PT/OT, imaging). |
| `payer_behavior_detector.py` | Composite payer fingerprinting using denial rate trends, payment velocity, and adjudication pattern shifts. Powers the `check_payer_behavior` MCP tool. |
| `synthetic_data_fixtures.py` | Public teaser fixtures for synthetic-data methodology. Excludes full commercial dataset catalog, scenario manifests, readiness reports, datasets, weights, and proprietary payer distributions. |

### `notebooks/` walkthroughs

| Notebook | What it teaches |
|---|---|
| `01_payer_clustering_walkthrough.ipynb` | End to end. Load CMS data, engineer features, run K-means clustering, visualize payer archetypes. |
| `02_patient_propensity_tutorial.ipynb` | End to end. Build a gradient boosted collectibility scorer from public claim attributes with SHAP explainability. |

### `data/`

No data is committed. See `data/README.md` for the public CMS datasets to download.

`sample_claims_schema.py` generates a 500 row synthetic CSV for local testing.

### Synthetic data methodology teasers

`reference/synthetic_data_fixtures.py` and `reference/synthetic-data-methodology.md` show how to discuss generated-from-scratch synthetic claims safely in public.

Included: representative specialties, a few public field examples, three scenario examples, and a safe denial-pattern walkthrough.

Excluded: full commercial dataset catalog, scenario manifests, readiness/moat reports, source coverage matrices, generated datasets, delivery artifacts, production weights, proprietary payer distributions, PHI, and customer data. Those belong behind Upstream Data paid API, service-token, or delivery gates.

---

## Methodology versus production

| Aspect | This repo | Production |
|---|---|---|
| Features | 15 public derivable features | 40 plus including payer behavioral graph and authorization policy state |
| Training data | CMS SynPUF (synthetic) | Live 835 remittance plus operator contributed signals |
| Model weights | Not included | Private |
| Drift detection | 3 statistical tests | 12 plus tests with payer specific thresholds |
| Clustering | Basic K-means, 5 features | Deep behavioral fingerprinting across the operator network, real time |
| Retraining | Manual | Automated weekly with data drift triggers |

---

## Install

```bash
pip install -r requirements.txt
```

Python 3.10 or later recommended.

---

## Quick start

### CARC code lookup

```python
from reference.carc_rarc_utils import parse_carc, group_by_category

info = parse_carc("97")
print(info.description)
# "The benefit for this service is included in the payment/allowance
#  for another service/procedure that has already been adjudicated."
print(info.corrective_action)
# "Review NCCI edits for the code pair. Add modifier 59 or X{EPSU}..."

info = parse_carc("CO-97")
# Same result. Handles prefixed codes from 835 files.

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
# DataFrame with cluster labels:
# "Aggressive Denier", "Slow Payer", "Prompt Payer", "Underpayer"
```

### Denial prediction

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

### Drift detection

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

### Authorization prediction

```python
import pandas as pd
from reference.aba_auth_predictor import predict_approval

# ABA example. Use the same pattern for other specialties by adjusting feature names.
auth_request = {
    "payer": "unitedhealthcare",
    "diagnosis_primary": "F84.0",
    "cpt_codes": ["97153", "97155"],
    "requested_units_weekly": 20,
    "patient_age": 7,
}

result = predict_approval(auth_request)
print(f"Approval probability: {result.probability:.1%}")
print(f"Top risk factors: {result.risk_factors}")
```

---

## Using with CMS SynPUF data

1. Download the 1 percent SynPUF sample from the [CMS website](https://www.cms.gov/data-research/statistics-trends-and-reports/medicare-claims-synthetic-public-use-files) (about 460MB).
2. Map the SynPUF columns to the schema in `sample_claims_schema.py`.
3. Run `notebooks/01_payer_clustering_walkthrough.ipynb`.

See `data/README.md` for all supported public datasets.

---

## What people ask

**Why publish this?**
The healthcare RCM community has historically operated as a black box. Vendors guard their methodology. Operators have no way to validate vendor claims. Upstream publishes the methodology so the community can learn from it, audit it, and contribute back.

**Can I run this on my own claims data?**
Not in public examples, shared notebooks, community fixtures, or synthetic-data tooling. Do not submit PHI, customer claims, customer data, or tenant data to this repository. If you adapt the reference methodology inside your own controlled environment, you are responsible for your own legal, security, privacy, and tenant-boundary controls.

**Will Upstream open source the production system?**
No. The production system contains operator contributed network signals, payer behavioral graphs trained on real time data, and customer specific tenant logic that cannot be extracted without compromising the network. The methodology is open. The production application stays private.

**How is this different from existing healthcare ML repos?**
Most existing repos use synthetic data without payer behavioral context. This repo treats payer behavior as the central object and provides the statistical tests Upstream uses to detect when behavior shifts.

**Can I contribute?**
Yes. See `CONTRIBUTING.md`. In scope: additional CARC and RARC codes, improved feature engineering, additional specialty templates for the auth predictor, notebooks demonstrating the reference implementations on additional public datasets, bug fixes, and documentation. Out of scope: anything requiring proprietary payer data or production internals.

---

## License

MIT. See `LICENSE`.

Upstream's production model weights, payer behavioral graph, and operator contributed signals stay private.

---

## Related

Part of the [Upstream Intelligence ecosystem](https://github.com/Upstream-Intelligence).

- [upstream-mcp](https://github.com/Upstream-Intelligence/upstream-mcp) — MCP server for Claude
- [upstream-skills](https://github.com/Upstream-Intelligence/upstream-skills) — Claude Code skills for billing teams
- **upstream-community** — you are here
- [awesome-payer-risk](https://github.com/Upstream-Intelligence/awesome-payer-risk) — curated RCM resources

Product: [upstream.cx](https://upstream.cx) · [Newsletter](https://upstream.cx/newsletter) · [Pricing](https://upstream.cx/pricing)

---

---

Built by [Upstream Intelligence](https://upstream.cx).

<div align="center">

**[upstream.cx](https://upstream.cx)** · hello@upstream.cx

Care Intelligence Platform.

</div>
