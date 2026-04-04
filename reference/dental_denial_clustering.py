"""
Dental Denial Clustering -- Reference Implementation

CDT code cluster detection for dental billing intelligence.
Detects downcoding patterns, bundling violations, frequency limit
violations, and silent PPO network alerts.

This methodology powers Upstream's Dental Pack intelligence engine.
"""

from __future__ import annotations

import uuid
from collections import defaultdict
from dataclasses import dataclass
from typing import Literal


ClusterType = Literal[
    "DOWNCODE",
    "BUNDLING",
    "FREQUENCY_LIMIT",
    "SILENT_PPO",
    "MISSING_PREDETERMINATION",
]

Severity = Literal["critical", "high", "medium"]

# Common CDT downcode pairs: billed code -> frequently paid-as code
KNOWN_DOWNCODE_PAIRS: dict[str, str] = {
    "D2750": "D2710",  # Crown PFM -> resin-based composite
    "D4341": "D4340",  # Periodontal scaling (complex) -> prophylaxis
    "D7210": "D7140",  # Surgical extraction -> simple extraction
    "D2712": "D2710",  # Crown 3/4 resin -> anterior composite
    "D4342": "D4341",  # 1-2 teeth perio -> full perio scaling
    "D6065": "D6061",  # Implant crown PFM -> implant crown metal
}

# Payers known for silent PPO behavior (paid < billed without explicit denial)
_SILENT_PPO_PAYERS = {"DELTA_DENTAL", "CIGNA_DENTAL", "METLIFE_DENTAL", "AETNA_DENTAL"}

# Threshold: downcode rate above this triggers a cluster flag
_DOWNCODE_RATE_THRESHOLD = 0.15

# Threshold: payment gap below billed that signals silent PPO (not an explicit denial)
_SILENT_PPO_UNDERPAYMENT_RATIO = 0.30


@dataclass
class DentalDenialRecord:
    claim_id: str
    cdt_code: str
    payer: str
    billed_amount: float
    paid_amount: float
    downcode_to: str | None  # CDT code it was paid as, if downcoded
    denial_reason: str  # free-text or payer remark code


@dataclass
class DentalCluster:
    cluster_type: ClusterType
    cdt_code: str
    payer: str
    occurrence_count: int
    revenue_impact: float
    severity: Severity
    cluster_id: str = ""

    def __post_init__(self) -> None:
        if not self.cluster_id:
            self.cluster_id = str(uuid.uuid4())[:8]


class DentalDenialClusterer:
    """
    Clusters dental denial records by CDT code and payer.

    Detects:
    - DOWNCODE: billed CDT paid as a lower-value code at above-threshold rate
    - SILENT_PPO: paid < billed by >30% with no explicit denial
    - BUNDLING: denial reason suggests bundling
    - FREQUENCY_LIMIT: denial reason suggests frequency/benefit limit
    - MISSING_PREDETERMINATION: denial for missing predetermination
    """

    def cluster(self, records: list[DentalDenialRecord]) -> list[DentalCluster]:
        clusters: list[DentalCluster] = []
        clusters.extend(self._detect_downcode_patterns(records))
        clusters.extend(self._detect_silent_ppo(records))
        clusters.extend(self._detect_by_denial_keyword(records, "bundl", "BUNDLING"))
        clusters.extend(
            self._detect_by_denial_keyword(records, "frequency", "FREQUENCY_LIMIT")
        )
        clusters.extend(
            self._detect_by_denial_keyword(
                records, "predetermination", "MISSING_PREDETERMINATION"
            )
        )
        clusters.sort(key=lambda c: c.revenue_impact, reverse=True)
        return clusters

    def _detect_downcode_patterns(
        self, records: list[DentalDenialRecord]
    ) -> list[DentalCluster]:
        """Flag CDT+payer buckets where downcode rate exceeds threshold."""
        # bucket: (cdt_code, payer) -> [records]
        buckets: dict[tuple[str, str], list[DentalDenialRecord]] = defaultdict(list)
        for r in records:
            if r.downcode_to:
                buckets[(r.cdt_code, r.payer)].append(r)

        all_by_bucket: dict[tuple[str, str], int] = defaultdict(int)
        for r in records:
            all_by_bucket[(r.cdt_code, r.payer)] += 1

        clusters = []
        for (cdt_code, payer), downcode_records in buckets.items():
            total = all_by_bucket[(cdt_code, payer)]
            rate = len(downcode_records) / total if total > 0 else 0.0
            if rate < _DOWNCODE_RATE_THRESHOLD:
                continue

            revenue_impact = sum(
                r.billed_amount - r.paid_amount for r in downcode_records
            )
            severity = _downcode_severity(rate)
            clusters.append(
                DentalCluster(
                    cluster_type="DOWNCODE",
                    cdt_code=cdt_code,
                    payer=payer,
                    occurrence_count=len(downcode_records),
                    revenue_impact=revenue_impact,
                    severity=severity,
                )
            )
        return clusters

    def _detect_silent_ppo(
        self, records: list[DentalDenialRecord]
    ) -> list[DentalCluster]:
        """
        Detect silent PPO behavior: paid < billed by > threshold with no
        explicit denial code. Common in plans with secondary PPO networks.
        """
        buckets: dict[tuple[str, str], list[DentalDenialRecord]] = defaultdict(list)
        for r in records:
            if r.downcode_to:
                continue  # already captured as downcode
            if not r.denial_reason.strip():
                gap_ratio = (
                    (r.billed_amount - r.paid_amount) / r.billed_amount
                    if r.billed_amount > 0
                    else 0.0
                )
                if gap_ratio > _SILENT_PPO_UNDERPAYMENT_RATIO:
                    buckets[(r.cdt_code, r.payer)].append(r)

        clusters = []
        for (cdt_code, payer), silent_records in buckets.items():
            if len(silent_records) < 3:
                continue
            revenue_impact = sum(
                r.billed_amount - r.paid_amount for r in silent_records
            )
            clusters.append(
                DentalCluster(
                    cluster_type="SILENT_PPO",
                    cdt_code=cdt_code,
                    payer=payer,
                    occurrence_count=len(silent_records),
                    revenue_impact=revenue_impact,
                    severity="high"
                    if payer.upper() in _SILENT_PPO_PAYERS
                    else "medium",
                )
            )
        return clusters

    def _detect_by_denial_keyword(
        self,
        records: list[DentalDenialRecord],
        keyword: str,
        cluster_type: ClusterType,
    ) -> list[DentalCluster]:
        """Group records whose denial reason contains a keyword."""
        buckets: dict[tuple[str, str], list[DentalDenialRecord]] = defaultdict(list)
        for r in records:
            if keyword.lower() in r.denial_reason.lower():
                buckets[(r.cdt_code, r.payer)].append(r)

        clusters = []
        for (cdt_code, payer), matched in buckets.items():
            if len(matched) < 2:
                continue
            revenue_impact = sum(r.billed_amount - r.paid_amount for r in matched)
            clusters.append(
                DentalCluster(
                    cluster_type=cluster_type,
                    cdt_code=cdt_code,
                    payer=payer,
                    occurrence_count=len(matched),
                    revenue_impact=revenue_impact,
                    severity="high",
                )
            )
        return clusters


def _downcode_severity(rate: float) -> Severity:
    if rate >= 0.40:
        return "critical"
    if rate >= 0.25:
        return "high"
    return "medium"


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    records: list[DentalDenialRecord] = []

    # Simulate Delta Dental D2750 -> D2710 downcode pattern (42% rate)
    for i in range(42):
        records.append(
            DentalDenialRecord(
                claim_id=f"DD{i:04d}",
                cdt_code="D2750",
                payer="DELTA_DENTAL",
                billed_amount=1200.0,
                paid_amount=480.0,  # paid as D2710
                downcode_to="D2710",
                denial_reason="",
            )
        )
    for i in range(42, 100):
        records.append(
            DentalDenialRecord(
                claim_id=f"DD{i:04d}",
                cdt_code="D2750",
                payer="DELTA_DENTAL",
                billed_amount=1200.0,
                paid_amount=1100.0,
                downcode_to=None,
                denial_reason="",
            )
        )

    # Simulate a few bundling denials
    for i in range(5):
        records.append(
            DentalDenialRecord(
                claim_id=f"BD{i:04d}",
                cdt_code="D4341",
                payer="CIGNA_DENTAL",
                billed_amount=300.0,
                paid_amount=0.0,
                downcode_to=None,
                denial_reason="Bundling violation -- included in D0150",
            )
        )

    clusterer = DentalDenialClusterer()
    clusters = clusterer.cluster(records)

    print(f"Found {len(clusters)} dental denial cluster(s):\n")
    for c in clusters:
        print(
            f"  [{c.severity.upper()}] {c.cluster_type} | "
            f"{c.cdt_code} | payer={c.payer} | "
            f"{c.occurrence_count} claims | ${c.revenue_impact:,.0f} impact"
        )
