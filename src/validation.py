"""
src/validation.py
=================
Validation and reconciliation module for data quality, financial identities,
and credit scorecard sanity checks.
"""

import logging
from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class DataQualityReport:
    """Collector and reporter for automated validation results."""

    def __init__(self):
        self.checks: List[Dict[str, Any]] = []

    def add_check(self, check_name: str, passed: bool, details: str = "", severity: str = "ERROR") -> None:
        self.checks.append({
            "check_name": check_name,
            "passed": passed,
            "details": details,
            "severity": severity
        })
        status_str = "PASSED" if passed else f"FAILED [{severity}]"
        logger.info("Validation Check: %s -> %s (%s)", check_name, status_str, details)

    def summary(self) -> Dict[str, Any]:
        total = len(self.checks)
        passed = sum(1 for c in self.checks if c["passed"])
        failed = total - passed
        return {
            "total_checks": total,
            "passed": passed,
            "failed": failed,
            "pass_rate": round(passed / total, 4) if total > 0 else 1.0,
            "checks": self.checks
        }


def validate_pnl_reconciliation(pnl_df: pd.DataFrame, report: Optional[DataQualityReport] = None) -> bool:
    """Validate that P&L accounting identities hold across all periods."""
    rep = report or DataQualityReport()
    all_passed = True

    # Check 1: Gross Profit = Revenue - COGS
    if "gross_profit" in pnl_df.columns and "revenue" in pnl_df.columns and "cogs" in pnl_df.columns:
        diff = (pnl_df["gross_profit"] - (pnl_df["revenue"] - pnl_df["cogs"])).abs().max()
        passed = diff < 1.0
        all_passed &= passed
        rep.add_check("P&L Gross Profit Identity", passed, f"Max diff: ${diff:.4f}")

    # Check 2: Net Profit reconciliation
    if "net_profit" in pnl_df.columns and "ebit" in pnl_df.columns:
        interest = pnl_df.get("interest_expense", 0.0)
        tax = pnl_df.get("tax", pnl_df.get("tax_expense", 0.0))
        calc_np = pnl_df["ebit"] - interest - tax
        diff = (pnl_df["net_profit"] - calc_np).abs().max()
        passed = diff < 1.0
        all_passed &= passed
        rep.add_check("P&L Net Profit Identity", passed, f"Max diff: ${diff:.4f}")

    return all_passed


def validate_balance_sheet_balance(bs_df: pd.DataFrame, report: Optional[DataQualityReport] = None) -> bool:
    """Validate that Total Assets = Total Liabilities + Equity across all periods."""
    rep = report or DataQualityReport()
    all_passed = True

    if "total_assets" in bs_df.columns and "total_liabilities_equity" in bs_df.columns:
        diff = (bs_df["total_assets"] - bs_df["total_liabilities_equity"]).abs().max()
        passed = diff < 1.0
        all_passed &= passed
        rep.add_check("Balance Sheet Identity (A = L + E)", passed, f"Max variance: ${diff:.4f}")

    return all_passed


def validate_budget_variance_math(var_df: pd.DataFrame, report: Optional[DataQualityReport] = None) -> bool:
    """Validate variance = actual - budget."""
    rep = report or DataQualityReport()
    
    if "variance" in var_df.columns and "actual" in var_df.columns and "budget" in var_df.columns:
        diff = (var_df["variance"] - (var_df["actual"] - var_df["budget"])).abs().max()
        passed = diff < 1.0
        rep.add_check("Budget Variance Arithmetic", passed, f"Max variance arithmetic diff: ${diff:.4f}")
        return passed
    return True


def validate_model_assumptions(eval_metrics: Dict[str, Any], report: Optional[DataQualityReport] = None) -> bool:
    """Validate statistical criteria for credit scorecard model approval."""
    rep = report or DataQualityReport()
    all_passed = True

    auc_val = eval_metrics.get("roc_auc", 0.0)
    passed_auc = auc_val >= 0.65
    all_passed &= passed_auc
    rep.add_check("Scorecard AUC Benchmark (>= 0.65)", passed_auc, f"AUC: {auc_val:.4f}")

    gini_val = eval_metrics.get("gini", 0.0)
    passed_gini = gini_val >= 0.30
    all_passed &= passed_gini
    rep.add_check("Scorecard Gini Benchmark (>= 0.30)", passed_gini, f"Gini: {gini_val:.4f}")

    ks_val = eval_metrics.get("ks_statistic", 0.0)
    passed_ks = ks_val >= 0.25
    all_passed &= passed_ks
    rep.add_check("Scorecard KS Separation (>= 0.25)", passed_ks, f"KS: {ks_val:.4f}")

    return all_passed


def validate_risk_band_coverage(bands_series: pd.Series, report: Optional[DataQualityReport] = None) -> bool:
    """Ensure all observations are assigned to a valid risk band with no nulls."""
    rep = report or DataQualityReport()
    valid_bands = {"Low Risk", "Medium Risk", "High Risk", "Very High Risk"}
    
    null_count = bands_series.isna().sum()
    invalid_count = (~bands_series.isin(valid_bands)).sum()
    passed = (null_count == 0) and (invalid_count == 0)

    rep.add_check(
        "Risk Band Coverage & Validity",
        passed,
        f"Nulls: {null_count}, Invalid bands: {invalid_count}"
    )
    return passed


def validate_expected_loss_range(
    el: np.ndarray,
    ead: np.ndarray,
    report: Optional[DataQualityReport] = None
) -> bool:
    """Ensure Expected Loss is strictly between 0 and EAD."""
    rep = report or DataQualityReport()
    passed_non_neg = (el >= 0).all()
    passed_bounded = (el <= ead + 1e-4).all()
    passed = passed_non_neg and passed_bounded

    rep.add_check(
        "Expected Loss Bound (0 <= EL <= EAD)",
        passed,
        f"Non-negative: {passed_non_neg}, Within EAD: {passed_bounded}"
    )
    return passed
