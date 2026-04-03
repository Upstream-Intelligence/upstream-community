"""Generate sample_claims.csv for testing reference implementations."""
import numpy as np
import pandas as pd
from pathlib import Path

np.random.seed(42)
n = 500

PAYERS = ["UnitedHealthcare", "Aetna", "BCBS", "Cigna", "Humana"]
CPT_CODES = ["97153", "97155", "97158", "97151", "97116", "99213", "99214", "97110"]
DIAGNOSES = ["F84.0", "F90.0", "F32.9", "M54.5", "Z00.00"]
PLACES = ["11", "12", "22", "03"]

denial_prob = {
    "UnitedHealthcare": 0.18,
    "Aetna": 0.22,
    "BCBS": 0.14,
    "Cigna": 0.20,
    "Humana": 0.16,
}

df = pd.DataFrame({
    "claim_date": pd.date_range("2024-01-01", periods=n, freq="D").to_list()[:n],
    "payer": np.random.choice(PAYERS, n),
    "cpt_code": np.random.choice(CPT_CODES, n),
    "diagnosis_group": [d[:3] for d in np.random.choice(DIAGNOSES, n)],
    "place_of_service": np.random.choice(PLACES, n),
    "billed_amount": np.random.lognormal(mean=5.5, sigma=0.8, size=n).round(2),
    "prior_denial_rate": np.random.beta(2, 8, size=n).round(4),
})

df["is_denied"] = [
    int(np.random.random() < denial_prob.get(payer, 0.18))
    for payer in df["payer"]
]

out_path = Path(__file__).parent / "sample_claims.csv"
df.to_csv(out_path, index=False)
print(f"Wrote {len(df)} rows to {out_path}")
