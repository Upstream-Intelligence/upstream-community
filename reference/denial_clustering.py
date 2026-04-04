"""
Denial Clustering -- Reference Implementation

Clusters denial patterns using CARC codes and aggregate billing data.
Includes the chi-square baseline comparison used to detect industry signals
(cross-customer anomalies where the same denial pattern affects multiple practices).

This is the methodology behind Upstream's Denial Cluster Map feature.
"""

from __future__ import annotations

import math
import uuid
from collections import defaultdict
from dataclasses import dataclass
from typing import Literal


# ---------------------------------------------------------------------------
# Root cause mapping (public CMS CARC codes)
# ---------------------------------------------------------------------------

CARC_ROOT_CAUSE_MAP: dict[str, str] = {
    "CO-4": "CODING_ERROR",
    "CO-16": "DOCUMENTATION_GAP",
    "CO-29": "TIMELY_FILING",
    "CO-50": "DOCUMENTATION_GAP",
    "CO-96": "POLICY_CHANGE",
    "CO-97": "CODING_ERROR",
    "CO-197": "AUTH_LAPSE",
    "CO-18": "CODING_ERROR",
    "CO-27": "CODING_ERROR",
    "PR-1": "UNDERPAYMENT",
    "PR-2": "UNDERPAYMENT",
    "PR-3": "UNDERPAYMENT",
    "OA-23": "UNDERPAYMENT",
}

# CPT code prefix -> clinical family
_CPT_FAMILY_PREFIXES: dict[str, str] = {
    "97": "ABA_THERAPY",
    "90": "BEHAVIORAL_HEALTH",
    "99": "EVALUATION_MANAGEMENT",
    "0": "PROCEDURE",
}

RootCause = Literal[
    "POLICY_CHANGE",
    "CODING_ERROR",
    "DOCUMENTATION_GAP",
    "AUTH_LAPSE",
    "TIMELY_FILING",
    "UNDERPAYMENT",
]


@dataclass
class DenialRecord:
    claim_id: str
    payer: str
    carc_code: str  # e.g. "CO-197"
    cpt_code: str
    billed_amount: float
    denied_date: str  # ISO date string


@dataclass
class DenialCluster:
    cluster_id: str
    root_cause: RootCause
    carc_code: str
    payer: str
    cpt_family: str
    claim_count: int
    dollar_impact: float
    cross_customer_signal: bool


class DenialClusterer:
    """
    Groups denial records by payer + CARC code and compares rates against a
    baseline window. Flags clusters that are statistically anomalous
    (z-score >= 2) as cross-customer industry signals.
    """

    def cluster(
        self,
        records: list[DenialRecord],
        baseline: list[DenialRecord],
    ) -> list[DenialCluster]:
        baseline_rates = self._compute_rates(baseline)
        current_rates = self._compute_rates(records)

        record_lookup: dict[tuple[str, str], list[DenialRecord]] = defaultdict(list)
        for r in records:
            record_lookup[(r.payer, r.carc_code)].append(r)

        clusters: list[DenialCluster] = []
        for (payer, carc), group in record_lookup.items():
            current_rate = current_rates.get((payer, carc), 0.0)
            baseline_rate = baseline_rates.get((payer, carc), 0.0)
            n = len(group)
            industry_signal = self._is_industry_signal(current_rate, baseline_rate, n)

            clusters.append(
                DenialCluster(
                    cluster_id=str(uuid.uuid4())[:8],
                    root_cause=self._classify_root_cause(carc),
                    carc_code=carc,
                    payer=payer,
                    cpt_family=_cpt_family(group[0].cpt_code),
                    claim_count=n,
                    dollar_impact=sum(r.billed_amount for r in group),
                    cross_customer_signal=industry_signal,
                )
            )

        clusters.sort(key=lambda c: c.dollar_impact, reverse=True)
        return clusters

    def _classify_root_cause(self, carc_code: str) -> RootCause:
        normalized = carc_code.upper().strip()
        cause = CARC_ROOT_CAUSE_MAP.get(normalized)
        if cause:
            return cause  # type: ignore[return-value]
        # Fallback heuristics by code number
        digits = normalized.lstrip("CO-").lstrip("PR-").lstrip("OA-")
        code_num = int(digits) if digits.isdigit() else 0
        if code_num in range(1, 10):
            return "UNDERPAYMENT"
        if code_num in range(10, 30):
            return "DOCUMENTATION_GAP"
        if code_num in range(190, 210):
            return "AUTH_LAPSE"
        return "POLICY_CHANGE"

    def _is_industry_signal(
        self,
        current_rate: float,
        baseline_rate: float,
        n: int,
    ) -> bool:
        """
        Returns True when the current rate is >= 2 standard deviations above
        the baseline rate (z-test for proportions, one-tailed).
        Requires at least 10 claims for the signal to be meaningful.
        """
        if n < 10 or baseline_rate <= 0.0:
            return False
        z = (current_rate - baseline_rate) / math.sqrt(
            baseline_rate * (1 - baseline_rate) / n
        )
        return z >= 2.0

    @staticmethod
    def _compute_rates(records: list[DenialRecord]) -> dict[tuple[str, str], float]:
        """Fraction of denials each payer+CARC bucket represents of that payer's total."""
        payer_totals: dict[str, int] = defaultdict(int)
        bucket_counts: dict[tuple[str, str], int] = defaultdict(int)
        for r in records:
            payer_totals[r.payer] += 1
            bucket_counts[(r.payer, r.carc_code)] += 1
        return {
            key: count / payer_totals[key[0]] for key, count in bucket_counts.items()
        }


def _cpt_family(cpt_code: str) -> str:
    for prefix, family in _CPT_FAMILY_PREFIXES.items():
        if cpt_code.startswith(prefix):
            return family
    return "OTHER"


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    baseline_records = [
        DenialRecord(f"B{i:04d}", "UHC", "CO-197", "97153", 250.0, "2024-01-15")
        for i in range(5)
    ] + [
        DenialRecord(f"B{i:04d}", "UHC", "CO-16", "97155", 180.0, "2024-01-20")
        for i in range(5, 30)
    ]

    current_records = [
        DenialRecord(f"C{i:04d}", "UHC", "CO-197", "97153", 250.0, "2024-04-10")
        for i in range(45)  # spike: CO-197 denial surge
    ] + [
        DenialRecord(f"C{i:04d}", "UHC", "CO-16", "97155", 180.0, "2024-04-15")
        for i in range(45, 60)
    ]

    clusterer = DenialClusterer()
    clusters = clusterer.cluster(current_records, baseline_records)

    print(f"Found {len(clusters)} denial cluster(s):\n")
    for c in clusters:
        signal = "INDUSTRY SIGNAL" if c.cross_customer_signal else "local"
        print(
            f"  [{signal}] {c.carc_code} | {c.root_cause} | "
            f"{c.claim_count} claims | ${c.dollar_impact:,.0f} impact | "
            f"payer={c.payer}"
        )
