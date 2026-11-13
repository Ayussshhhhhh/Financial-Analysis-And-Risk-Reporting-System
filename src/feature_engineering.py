"""
src/feature_engineering.py
===========================
Feature engineering module for the Financial Analytics and Risk Reporting System.

Provides functions to build credit risk features, compute Weight of Evidence (WOE)
and Information Value (IV) for scorecard development.
"""

import logging
import warnings
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
GRADE_NUMERIC: Dict[str, int] = {"A": 1, "B": 2, "C": 3, "D": 4, "E": 5, "F": 6, "G": 7}

HIGH_RISK_PURPOSES = {"debt_consolidation", "credit_card"}

DTI_BINS = [0, 15, 25, 35, float("inf")]
DTI_LABELS = ["0-15", "15-25", "25-35", "35+"]

REVOL_UTIL_BINS = [0, 20, 40, 60, 80, float("inf")]
REVOL_UTIL_LABELS = ["0-20%", "20-40%", "40-60%", "60-80%", "80%+"]


# ---------------------------------------------------------------------------
# Loan feature creator
# ---------------------------------------------------------------------------
def create_loan_features(df: pd.DataFrame) -> pd.DataFrame:
    """Create derived credit risk features from the cleaned loan DataFrame.

    New columns added:
    - ``loan_to_income``       : loan_amnt / annual_inc
    - ``dti_bucket``           : categorical DTI band
    - ``income_bucket``        : quantile-based income band (Q1–Q4)
    - ``emp_length_numeric``   : numeric employment years (0 if < 1 yr)
    - ``revol_util_bucket``    : categorical revolving utilisation band
    - ``grade_numeric``        : integer encoding of loan grade (A=1 … G=7)
    - ``is_high_risk_purpose`` : 1 if purpose is debt_consolidation or credit_card
    - ``inq_rate``             : inq_last_6mths / (open_acc + 1) — inquiry rate proxy

    Args:
        df: Cleaned loan DataFrame.

    Returns:
        DataFrame with additional feature columns.
    """
    df = df.copy()

    # loan_to_income
    if "loan_amnt" in df.columns and "annual_inc" in df.columns:
        df["loan_to_income"] = np.where(
            df["annual_inc"] > 0,
            df["loan_amnt"] / df["annual_inc"],
            np.nan,
        )
        logger.debug("Created loan_to_income. Mean=%.3f", df["loan_to_income"].mean())

    # DTI bucket
    if "dti" in df.columns:
        df["dti_bucket"] = pd.cut(
            df["dti"],
            bins=DTI_BINS,
            labels=DTI_LABELS,
            right=False,
            include_lowest=True,
        ).astype(str)
        logger.debug("Created dti_bucket.")

    # Income bucket (quantile-based)
    if "annual_inc" in df.columns:
        try:
            df["income_bucket"] = pd.qcut(
                df["annual_inc"],
                q=4,
                labels=["Q1-Low", "Q2-Mid-Low", "Q3-Mid-High", "Q4-High"],
                duplicates="drop",
            ).astype(str)
        except ValueError:
            df["income_bucket"] = "Q1-Low"
        logger.debug("Created income_bucket.")

    # Employment length numeric
    if "emp_length" in df.columns:
        if df["emp_length"].dtype in [np.float64, np.int64]:
            df["emp_length_numeric"] = df["emp_length"]
        else:
            import re as _re

            def _emp_to_num(val: Any) -> Optional[float]:
                s = str(val).strip().lower()
                if s in ("nan", "n/a", ""):
                    return np.nan
                if "< 1" in s:
                    return 0.0
                match = _re.search(r"(\d+)", s)
                return float(match.group(1)) if match else np.nan

            df["emp_length_numeric"] = df["emp_length"].apply(_emp_to_num)
        logger.debug("Created emp_length_numeric.")

    # Revolving utilization bucket
    if "revol_util" in df.columns:
        df["revol_util_bucket"] = pd.cut(
            df["revol_util"],
            bins=REVOL_UTIL_BINS,
            labels=REVOL_UTIL_LABELS,
            right=False,
            include_lowest=True,
        ).astype(str)
        logger.debug("Created revol_util_bucket.")

    # Grade numeric
    if "grade" in df.columns:
        df["grade_numeric"] = df["grade"].map(GRADE_NUMERIC)
        logger.debug("Created grade_numeric.")

    # High-risk purpose flag
    if "purpose" in df.columns:
        df["is_high_risk_purpose"] = df["purpose"].apply(
            lambda p: 1 if str(p).lower().replace(" ", "_") in HIGH_RISK_PURPOSES else 0
        )
        logger.debug(
            "Created is_high_risk_purpose. Count=%d", df["is_high_risk_purpose"].sum()
        )

    # Inquiry rate proxy
    if "inq_last_6mths" in df.columns and "open_acc" in df.columns:
        df["inq_rate"] = df["inq_last_6mths"] / (df["open_acc"].clip(lower=0) + 1)
        logger.debug("Created inq_rate.")

    logger.info("Feature engineering complete. Shape: %s", df.shape)
    return df


# ---------------------------------------------------------------------------
# WOE binning
# ---------------------------------------------------------------------------
def woe_binning(
    df: pd.DataFrame,
    feature: str,
    target: str,
    n_bins: int = 10,
) -> pd.Series:
    """Bin a continuous feature into *n_bins* quantile-based bins.

    For categorical features the original values are preserved.

    Args:
        df: DataFrame containing the feature and target.
        feature: Column name to bin.
        target: Binary target column (0/1).
        n_bins: Number of bins for continuous features.

    Returns:
        Series of string bin labels aligned to df's index.
    """
    series = df[feature].copy()
    if pd.api.types.is_numeric_dtype(series):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            try:
                binned = pd.qcut(series, q=n_bins, duplicates="drop")
            except ValueError:
                # Fallback to equal-width if quantiles can't be computed
                binned = pd.cut(series, bins=n_bins, include_lowest=True)
        return binned.astype(str)
    else:
        return series.astype(str)


# ---------------------------------------------------------------------------
# WOE / IV calculator
# ---------------------------------------------------------------------------
def calculate_woe_iv(
    df: pd.DataFrame,
    feature: str,
    target: str,
    bins: Optional[pd.Series] = None,
    n_bins: int = 10,
) -> Dict[str, Any]:
    """Compute WOE table and Information Value for a single feature.

    Args:
        df: DataFrame with feature and target columns.
        feature: Predictor column name.
        target: Binary target column name (0=good, 1=bad/default).
        bins: Pre-computed bin series. If None, computed via woe_binning().
        n_bins: Number of bins if *bins* is not provided.

    Returns:
        Dictionary with keys:
        - ``feature``    : feature name
        - ``iv``         : total Information Value (float)
        - ``woe_table``  : DataFrame with columns: bin, n, events, non_events,
                           pct_events, pct_non_events, woe, iv_contribution
        - ``strength``   : IV strength label (Useless/Weak/Medium/Strong/Suspicious)
    """
    _validate_target(df, target)

    if bins is None:
        bins = woe_binning(df, feature, target, n_bins=n_bins)

    temp = pd.DataFrame({"bin": bins, "target": df[target]}).dropna()
    total_events = temp["target"].sum()
    total_non_events = (temp["target"] == 0).sum()

    if total_events == 0 or total_non_events == 0:
        logger.warning("Feature '%s': no events or non-events — IV undefined.", feature)
        return {"feature": feature, "iv": np.nan, "woe_table": pd.DataFrame(), "strength": "Undefined"}

    woe_rows = []
    for bin_label, group in temp.groupby("bin", observed=True):
        n = len(group)
        events = group["target"].sum()
        non_events = n - events
        pct_ev = (events + 0.5) / (total_events + 0.5)
        pct_nev = (non_events + 0.5) / (total_non_events + 0.5)
        woe_val = np.log(pct_ev / pct_nev)
        iv_contrib = (pct_ev - pct_nev) * woe_val
        woe_rows.append({
            "bin": bin_label,
            "n": n,
            "events": events,
            "non_events": non_events,
            "pct_events": round(events / total_events, 6),
            "pct_non_events": round(non_events / total_non_events, 6),
            "woe": round(woe_val, 6),
            "iv_contribution": round(iv_contrib, 6),
        })

    woe_table = pd.DataFrame(woe_rows)
    iv = round(woe_table["iv_contribution"].sum(), 6)

    if iv < 0.02:
        strength = "Useless"
    elif iv < 0.1:
        strength = "Weak"
    elif iv < 0.3:
        strength = "Medium"
    elif iv < 0.5:
        strength = "Strong"
    else:
        strength = "Suspicious (too strong)"

    logger.debug("Feature '%s': IV=%.4f (%s)", feature, iv, strength)
    return {"feature": feature, "iv": iv, "woe_table": woe_table, "strength": strength}


# ---------------------------------------------------------------------------
# Bulk WOE / IV summary
# ---------------------------------------------------------------------------
def calculate_all_woe_iv(
    df: pd.DataFrame,
    features: List[str],
    target: str,
    n_bins: int = 10,
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Calculate WOE and IV for all specified features.

    Args:
        df: DataFrame containing features and target.
        features: List of feature column names.
        target: Binary target column name.
        n_bins: Number of quantile bins for continuous features.

    Returns:
        Tuple of:
        - ``summary_df`` : DataFrame indexed by feature with iv, strength, n_bins columns.
        - ``detail``     : Dict mapping feature name → full WOE result dict.
    """
    _validate_target(df, target)
    summary_rows = []
    detail: Dict[str, Any] = {}

    for feat in features:
        if feat not in df.columns:
            logger.warning("Feature '%s' not found in DataFrame — skipped.", feat)
            continue
        result = calculate_woe_iv(df, feat, target, n_bins=n_bins)
        detail[feat] = result
        summary_rows.append({
            "feature": feat,
            "iv": result["iv"],
            "strength": result["strength"],
            "n_bins": len(result["woe_table"]),
        })

    summary_df = (
        pd.DataFrame(summary_rows)
        .sort_values("iv", ascending=False)
        .reset_index(drop=True)
    )
    logger.info("WOE/IV computed for %d features.", len(summary_df))
    return summary_df, detail


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _validate_target(df: pd.DataFrame, target: str) -> None:
    """Raise ValueError if target column is absent or not binary."""
    if target not in df.columns:
        raise ValueError(f"Target column '{target}' not found in DataFrame.")
    unique_vals = set(df[target].dropna().unique())
    if not unique_vals.issubset({0, 1, 0.0, 1.0}):
        raise ValueError(
            f"Target column '{target}' must be binary (0/1). Found: {unique_vals}"
        )
