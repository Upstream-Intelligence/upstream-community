"""
Public synthetic data methodology fixtures for Upstream Data.

This module intentionally publishes a small teaser fixture set. It demonstrates
safe methodology without exposing the full commercial pack catalog, buyer
scenario library, source coverage matrix, generated datasets, production model
weights, proprietary payer distributions, customer data, PHI, or record-anonymized
patient records.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass

FORBIDDEN_FIELDS = frozenset(
    {
        "patient_name",
        "member_name",
        "date_of_birth",
        "dob",
        "ssn",
        "mrn",
        "medical_record_number",
        "raw_claim_text",
        "raw_diagnosis_text",
        "raw_email_body",
    }
)

PUBLIC_SOURCE_CATEGORIES = (
    "claims_standard",
    "authorization",
    "payment_system",
    "coverage_policy",
    "synthetic_quality",
)

PUBLIC_TEASER_SCENARIOS = (
    "authorization-surge",
    "documentation-crackdown",
    "reimbursement-slowdown",
)


@dataclass(frozen=True)
class SyntheticPackTeaser:
    pack_family: str
    representative_pack: str
    public_field_examples: tuple[str, ...]
    public_scenarios: tuple[str, ...] = PUBLIC_TEASER_SCENARIOS
    synthetic_only: bool = True
    no_phi: bool = True
    no_customer_data: bool = True

    def to_dict(self) -> dict:
        payload = asdict(self)
        assert_public_safe_fixture(payload)
        return payload


PUBLIC_TEASER_FIXTURES: tuple[SyntheticPackTeaser, ...] = (
    SyntheticPackTeaser(
        pack_family="behavioral_health",
        representative_pack="aba",
        public_field_examples=("authorization_window_days", "therapy_unit_type"),
    ),
    SyntheticPackTeaser(
        pack_family="dental",
        representative_pack="dental",
        public_field_examples=("procedure_category", "fee_schedule_variance_band"),
    ),
    SyntheticPackTeaser(
        pack_family="facility",
        representative_pack="snf-ma",
        public_field_examples=("length_of_stay_band", "ma_contract_variance_band"),
    ),
    SyntheticPackTeaser(
        pack_family="home_based_care",
        representative_pack="home-health",
        public_field_examples=("certification_period_day", "noa_timing_band"),
    ),
    SyntheticPackTeaser(
        pack_family="outpatient",
        representative_pack="pt-ot",
        public_field_examples=("therapy_discipline", "visit_limit_remaining"),
    ),
)


def assert_public_safe_fixture(payload: dict) -> None:
    keys = {str(key).lower() for key in payload.keys()}
    forbidden = keys & FORBIDDEN_FIELDS
    if forbidden:
        raise ValueError(f"Fixture contains forbidden PHI-like fields: {sorted(forbidden)}")


def list_synthetic_pack_teasers() -> list[dict]:
    """Return public teaser fixtures only, not the full commercial catalog."""
    return [fixture.to_dict() for fixture in PUBLIC_TEASER_FIXTURES]


def synthetic_public_pack_teasers() -> list[dict]:
    """Canonical public-safe teaser helper expected by upstream-data audits."""
    return list_synthetic_pack_teasers()


def synthetic_marketplace_catalog_reference() -> dict:
    """Return a public methodology reference without commercial pack depth."""
    payload = {
        "catalog_surface": "public teaser methodology only",
        "representative_pack_count": len(PUBLIC_TEASER_FIXTURES),
        "representative_packs": [fixture.representative_pack for fixture in PUBLIC_TEASER_FIXTURES],
        "excluded_from_public": (
            "full commercial pack catalog",
            "generated datasets",
            "paid scenario manifests",
            "readiness scorecards",
            "payer archetype weights",
            "contract simulation details",
            "release ledgers",
            "customer-specific synthetic twins",
        ),
        "synthetic_only": True,
        "no_phi": True,
        "no_customer_data": True,
    }
    assert_public_safe_fixture(payload)
    return payload


def synthetic_guardrail_reference() -> dict:
    """Return the public/private boundary language for community examples."""
    return {
        "allowed_public_surface": (
            "schema examples",
            "tiny synthetic teaser fixtures",
            "methodology explanation",
            "public source category descriptions",
        ),
        "paid_or_private_surface": (
            "full datasets",
            "scenario depth",
            "adjudication traces",
            "transaction/event corpora",
            "agent evaluation tasks",
            "payer archetype weights",
            "contract and fee schedule simulation",
            "release ledgers",
            "enterprise configs",
        ),
        "required_language": (
            "generated-from-scratch synthetic data",
            "no PHI",
            "no customer data",
            "no real-payer-truth claims",
        ),
    }


def build_denial_pattern_walkthrough(
    pack_family: str = "behavioral_health",
    scenario: str = "authorization-surge",
) -> dict:
    """Build a safe, non-commercial-depth denial-pattern walkthrough."""
    if scenario not in PUBLIC_TEASER_SCENARIOS:
        raise KeyError(
            "Only public teaser scenarios are available in upstream-community. "
            "Full scenario manifests are served by paid Upstream Data APIs."
        )
    fixture = next(
        (item for item in PUBLIC_TEASER_FIXTURES if item.pack_family == pack_family),
        None,
    )
    if fixture is None:
        raise KeyError(f"Unknown public teaser pack family: {pack_family}")

    return {
        "pack_family": pack_family,
        "representative_pack": fixture.representative_pack,
        "scenario": scenario,
        "synthetic_claim_id": f"syn-{fixture.representative_pack}-claim-0001",
        "synthetic_payer_archetype": "commercial_like",
        "denial_pattern": {
            "denial_reason_family": "authorization",
            "denial_carc_code": "197",
            "appeal_outcome": "partially_overturned",
        },
        "public_field_examples": fixture.public_field_examples,
        "public_source_categories": PUBLIC_SOURCE_CATEGORIES,
        "paywalled_depth": (
            "full commercial pack catalog",
            "full scenario manifests",
            "source coverage matrices",
            "readiness and moat reports",
            "generated datasets and delivery artifacts",
        ),
        "guardrails": (
            "generated-from-scratch synthetic data",
            "no PHI or customer data",
            "no production model weights",
            "no proprietary payer distributions",
        ),
    }


if __name__ == "__main__":
    from pprint import pprint

    pprint(build_denial_pattern_walkthrough())
