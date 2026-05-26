# Synthetic Data Methodology Fixtures

These fixtures document how Upstream Data packs can be used for public QA, demos, and agent evaluation without exposing PHI, customer data, production model weights, proprietary payer distributions, or the full commercial pack catalog.

## What Is Included

- A small representative teaser set across broad pack families
- Public-safe schema field examples with only 1-2 fields per family
- Three public scenario examples: authorization surge, documentation crackdown, and reimbursement slowdown
- Source/provenance categories that explain plausibility limits
- A denial-pattern walkthrough that uses only synthetic identifiers

## What Is Excluded

- Full commercial pack catalog depth
- Full buyer scenario manifests
- Pack readiness and moat reports
- Source coverage matrices
- Provider, fulfillment, publication, and delivery contracts
- Production model weights
- Proprietary payer behavioral graphs
- Customer claims, EOBs, notes, or exports
- PHI or de-identified patient records
- Claims that synthetic fixtures represent observed payer truth

## Reproducible Example

```python
from reference.synthetic_data_fixtures import build_denial_pattern_walkthrough

walkthrough = build_denial_pattern_walkthrough("behavioral_health", "authorization-surge")
print(walkthrough["synthetic_claim_id"])
print(walkthrough["denial_pattern"]["denial_carc_code"])
```

Expected output uses synthetic identifiers like `syn-aba-claim-0001`.

## Safety Language

Use this wording when publishing examples:

- "Generated-from-scratch synthetic data."
- "No PHI and no customer data."
- "Public sources calibrate schema, plausibility, and methodology, not proprietary payer frequency truth."

Avoid this wording:

- "HIPAA de-identified patient data"
- "Real payer truth"
- "Customer-derived claims"
- "Observed commercial payer distribution"
