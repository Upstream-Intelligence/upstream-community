"""
CARC/RARC denial code utilities.

Uses the publicly available CMS claim adjustment reason code list.
No proprietary data required — all codes and descriptions are public.

Usage:
    from reference.carc_rarc_utils import parse_carc, group_by_category

    info = parse_carc("97")
    print(info.description)     # "The benefit for this service is included in..."
    print(info.corrective_action)
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional


@dataclass
class CARCInfo:
    code: str
    category: str           # "contractual_obligation", "patient_responsibility", etc.
    description: str
    common_cause: str
    corrective_action: str
    regulatory_basis: Optional[str] = None


# Subset of CMS CARC codes (public domain — full list at cms.gov/medicare/coding-billing)
_CARC_REGISTRY: dict[str, CARCInfo] = {
    "1": CARCInfo(
        code="1",
        category="contractual_obligation",
        description="Deductible amount",
        common_cause="Patient has not met annual deductible",
        corrective_action="Bill patient for deductible amount; verify eligibility before service",
    ),
    "16": CARCInfo(
        code="16",
        category="claim_information_missing",
        description="Claim/service lacks information or has submission/billing error(s).",
        common_cause="Missing required field: NPI, place of service, or diagnosis code",
        corrective_action="Review rejection notice for specific missing field; correct and resubmit",
        regulatory_basis="45 CFR 162.1102",
    ),
    "18": CARCInfo(
        code="18",
        category="duplicate",
        description="Exact duplicate claim/service.",
        common_cause="Claim submitted twice; clearinghouse resubmission; billing system error",
        corrective_action=(
            "Check claim history; if true duplicate, no action needed. "
            "If rebill, add appropriate modifier and resubmit."
        ),
    ),
    "29": CARCInfo(
        code="29",
        category="timely_filing",
        description="The time limit for filing has expired.",
        common_cause="Claim not submitted within payer's timely filing window",
        corrective_action=(
            "Appeal with proof of timely filing (clearinghouse acceptance report, "
            "EDI acknowledgment, or certified mail receipt)"
        ),
    ),
    "50": CARCInfo(
        code="50",
        category="non_covered",
        description="These are non-covered services because this is not deemed a medical necessity.",
        common_cause="Missing or insufficient medical necessity documentation; LCD/NCD criteria not met",
        corrective_action=(
            "Obtain and submit supporting clinical documentation; "
            "reference applicable LCD/NCD policy in appeal letter"
        ),
        regulatory_basis="42 CFR 411.406",
    ),
    "96": CARCInfo(
        code="96",
        category="non_covered",
        description="Non-covered charge(s).",
        common_cause="Service not covered under patient's plan; benefit exclusion",
        corrective_action=(
            "Verify patient benefits; if covered, appeal with EOB and benefit documentation. "
            "If excluded, bill patient."
        ),
    ),
    "97": CARCInfo(
        code="97",
        category="bundled",
        description=(
            "The benefit for this service is included in the payment/allowance "
            "for another service/procedure that has already been adjudicated."
        ),
        common_cause="Unbundling of services; component billed separately from comprehensive code",
        corrective_action=(
            "Review NCCI edits for the code pair. "
            "Add modifier -59 or -X{EPSU} if services are clinically distinct and separately documented."
        ),
        regulatory_basis="NCCI Policy Manual Chapter 1",
    ),
    "197": CARCInfo(
        code="197",
        category="authorization",
        description="Precertification/authorization/notification/pre-treatment absent.",
        common_cause="Prior auth not obtained before service; auth not linked to claim",
        corrective_action=(
            "Obtain retro-authorization if payer allows; "
            "if retro-auth denied, appeal with medical necessity documentation and payer authorization policy"
        ),
    ),
    "4": CARCInfo(
        code="4",
        category="modifier_issue",
        description="The procedure code is inconsistent with the modifier used.",
        common_cause="Incorrect modifier applied; modifier not appropriate for the procedure code",
        corrective_action="Review modifier requirements; correct modifier and resubmit",
    ),
    "27": CARCInfo(
        code="27",
        category="eligibility",
        description="Expenses incurred after coverage terminated.",
        common_cause="Service date after patient's coverage end date",
        corrective_action=(
            "Verify eligibility on date of service; "
            "if coverage was active, appeal with eligibility verification documentation"
        ),
    ),
}


def parse_carc(code: str) -> Optional[CARCInfo]:
    """Return structured information for a CARC code.

    Args:
        code: CARC code string (e.g. "97", "CO-97", "16")

    Returns:
        CARCInfo if found, None otherwise
    """
    # Normalize: strip leading CO-/PR-/OA-/PI- prefixes
    normalized = code.strip().upper()
    for prefix in ("CO-", "PR-", "OA-", "PI-"):
        if normalized.startswith(prefix):
            normalized = normalized[len(prefix):]
            break

    return _CARC_REGISTRY.get(normalized)


def group_by_category(codes: list[str]) -> dict[str, list[CARCInfo]]:
    """Group a list of CARC codes by denial category.

    Useful for identifying systemic denial patterns — if multiple codes
    share a category (e.g. "authorization"), that signals a process issue.

    Args:
        codes: List of CARC code strings

    Returns:
        Dict mapping category name to list of CARCInfo objects
    """
    result: dict[str, list[CARCInfo]] = {}
    for code in codes:
        info = parse_carc(code)
        if info:
            result.setdefault(info.category, []).append(info)
    return result


def denial_frequency_report(codes: list[str]) -> list[tuple[str, int, Optional[CARCInfo]]]:
    """Count and rank denial codes by frequency.

    Args:
        codes: List of CARC codes (may contain duplicates)

    Returns:
        List of (code, count, info) sorted by frequency descending
    """
    from collections import Counter
    counts = Counter(
        code.strip().upper().lstrip("CO-").lstrip("PR-") for code in codes
    )
    return [
        (code, count, parse_carc(code))
        for code, count in counts.most_common()
    ]
