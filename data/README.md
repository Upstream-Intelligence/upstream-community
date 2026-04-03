# Data Sources

All notebooks and reference implementations use only **public data**. No PHI. No proprietary payer data.

## CMS SynPUF (Synthetic Public Use Files)

Synthetic Medicare claims data based on real claim structures but with randomized beneficiary information.

- Download: https://www.cms.gov/data-research/statistics-trends-and-reports/medicare-claims-synthetic-public-use-files
- Use: Denial prediction model training (`01_denial_prediction_walkthrough.ipynb`)
- Size: ~2.3GB for 5% sample; use 1% sample (~460MB) for local development

## CMS 835 Transaction Reference Data

CARC and RARC code lists (public domain).

- Download: https://www.cms.gov/medicare/coding-billing/claim-adjustment-reason-codes
- Use: `carc_rarc_utils.py` registry, `04_carc_denial_distribution.ipynb`

## CMS Medicare Fee Schedule

National physician fee schedule by CPT code.

- Download: https://www.cms.gov/medicare/payment/fee-schedules/physician
- Use: Fee schedule lookups, reimbursement benchmarking

## CMS Medicare Claims Summary Files

Aggregated Medicare claims by county, specialty, and procedure.

- Download: https://data.cms.gov/summary-statistics-on-use-and-payments
- Use: Payer drift detection baseline (`02_payer_drift_detection.ipynb`)

## Sample Data

`sample_claims.csv` — 500 synthetic claims with the schema expected by the reference implementations. Not real patient data.
