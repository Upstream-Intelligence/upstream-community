"""
Payer behavioral drift detection.

Detects when a payer changes their denial behavior — the core signal
that Upstream's DriftWatch engine is built on.

Algorithm:
- Baseline window: 90 days of historical claims
- Detection window: 7 days of recent claims
- Statistical tests: chi-square (categorical) + KS (continuous)
- Alert threshold: p < 0.01 in >20% of features

Uses only public-compatible data structures.

Requirements:
    pip install pandas numpy scipy
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats
from dataclasses import dataclass, field


@dataclass
class DriftAlert:
    payer: str
    feature: str
    test_type: str          # "chi_square" or "ks"
    p_value: float
    baseline_rate: float
    current_rate: float
    relative_change: float  # (current - baseline) / baseline


@dataclass
class DriftReport:
    payer: str
    baseline_days: int
    detection_days: int
    alerts: list[DriftAlert] = field(default_factory=list)
    features_tested: int = 0

    @property
    def drift_detected(self) -> bool:
        """Alert when >20% of features show significant drift."""
        if self.features_tested == 0:
            return False
        return len(self.alerts) / self.features_tested > 0.20

    @property
    def alert_rate(self) -> float:
        if self.features_tested == 0:
            return 0.0
        return len(self.alerts) / self.features_tested


def detect_drift(
    payer: str,
    baseline_df: pd.DataFrame,
    current_df: pd.DataFrame,
    p_threshold: float = 0.01,
) -> DriftReport:
    """Detect behavioral drift for a single payer.

    Args:
        payer: Payer name for reporting
        baseline_df: Historical claims (90-day window)
        current_df: Recent claims (7-day window)
        p_threshold: Significance threshold (default 0.01)

    Both DataFrames expected to have columns:
        - denial_rate (float 0-1, per CPT+date group)
        - top_carc_code (str, most common denial reason)
        - payment_rate (float, % of billed paid)
        - cpt_distribution (str, comma-joined CPT codes)
    """
    report = DriftReport(
        payer=payer,
        baseline_days=len(baseline_df),
        detection_days=len(current_df),
    )

    # --- Continuous: denial rate (KS test) ---
    if "denial_rate" in baseline_df.columns and len(current_df) >= 5:
        stat, p = stats.ks_2samp(
            baseline_df["denial_rate"].dropna(),
            current_df["denial_rate"].dropna(),
        )
        baseline_mean = baseline_df["denial_rate"].mean()
        current_mean = current_df["denial_rate"].mean()
        relative_change = (
            (current_mean - baseline_mean) / baseline_mean
            if baseline_mean > 0 else 0.0
        )

        report.features_tested += 1
        if p < p_threshold:
            report.alerts.append(DriftAlert(
                payer=payer,
                feature="denial_rate",
                test_type="ks",
                p_value=float(p),
                baseline_rate=float(baseline_mean),
                current_rate=float(current_mean),
                relative_change=float(relative_change),
            ))

    # --- Categorical: top CARC code distribution (chi-square) ---
    if "top_carc_code" in baseline_df.columns:
        baseline_counts = baseline_df["top_carc_code"].value_counts()
        current_counts = current_df["top_carc_code"].value_counts()

        # Align on same categories
        all_codes = baseline_counts.index.union(current_counts.index)
        baseline_aligned = baseline_counts.reindex(all_codes, fill_value=0)
        current_aligned = current_counts.reindex(all_codes, fill_value=0)

        # Chi-square requires expected counts >= 5 — skip if too sparse
        if baseline_aligned.sum() >= 5 and current_aligned.sum() >= 5:
            # Scale current to same total as baseline for chi-square
            scale = baseline_aligned.sum() / current_aligned.sum()
            _, p = stats.chisquare(
                current_aligned * scale,
                f_exp=baseline_aligned,
            )

            report.features_tested += 1
            if p < p_threshold:
                top_baseline = str(baseline_counts.index[0]) if len(baseline_counts) > 0 else "N/A"
                top_current = str(current_counts.index[0]) if len(current_counts) > 0 else "N/A"
                report.alerts.append(DriftAlert(
                    payer=payer,
                    feature="carc_distribution",
                    test_type="chi_square",
                    p_value=float(p),
                    baseline_rate=float(baseline_counts.iloc[0] / baseline_counts.sum()) if len(baseline_counts) > 0 else 0.0,
                    current_rate=float(current_counts.iloc[0] / current_counts.sum()) if len(current_counts) > 0 else 0.0,
                    relative_change=0.0,
                ))

    # --- Continuous: payment rate (KS test) ---
    if "payment_rate" in baseline_df.columns and len(current_df) >= 5:
        stat, p = stats.ks_2samp(
            baseline_df["payment_rate"].dropna(),
            current_df["payment_rate"].dropna(),
        )
        baseline_mean = baseline_df["payment_rate"].mean()
        current_mean = current_df["payment_rate"].mean()

        report.features_tested += 1
        if p < p_threshold:
            report.alerts.append(DriftAlert(
                payer=payer,
                feature="payment_rate",
                test_type="ks",
                p_value=float(p),
                baseline_rate=float(baseline_mean),
                current_rate=float(current_mean),
                relative_change=float(
                    (current_mean - baseline_mean) / baseline_mean
                    if baseline_mean > 0 else 0.0
                ),
            ))

    return report
