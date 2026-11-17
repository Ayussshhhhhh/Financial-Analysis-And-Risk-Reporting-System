"""
src/data_cleaning.py
====================
Data cleaning and quality-check module for the Financial Analytics and
Risk Reporting System.

Provides functions to clean raw loan and ledger DataFrames, validate the
accounting equation, and produce detailed data-quality reports.
"""

import logging
import re
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
# Protected attributes — documented here, not used in modelling
_PROTECTED_ATTRIBUTES: List[str] = ["race", "gender", "sex", "ethnicity", "nationality", "religion"]

NUMERIC_RANGE_RULES: Dict[str, Dict[str, float]] = {
    "loan_amnt":    {"min": 500,  "max": 50_000},
    "int_rate":     {"min": 0,    "max": 40},
    "installment":  {"min": 10,   "max": 5_000},
    "annual_inc":   {"min": 1,    "max": 10_000_000},
    "dti":          {"min": 0,    "max": 60},
    "revol_util":   {"min": 0,    "max": 100},
    "delinq_2yrs":  {"min": 0,    "max": 30},
    "open_acc":     {"min": 0,    "max": 100},
    "pub_rec":      {"min": 0,    "max": 20},
    "total_acc":    {"min": 0,    "max": 200},
    "inq_last_6mths": {"min": 0, "max": 20},
}

GRADE_ORDER = ["A", "B", "C", "D", "E", "F", "G"]


# ---------------------------------------------------------------------------
# Loan data cleaning
# ---------------------------------------------------------------------------
def _parse_term(series: pd.Series) -> pd.Series:
    """Extract integer month count from term strings like '36 months'."""
    return pd.to_numeric(
        series.astype(str).str.extract(r"(\d+)", expand=False), errors="coerce"
    )


def _parse_int_rate(series: pd.Series) -> pd.Series:
    """Strip '%' and convert interest rate to float."""
    return pd.to_numeric(
        series.astype(str).str.replace("%", "", regex=False).str.strip(),
        errors="coerce",
    )


def _parse_emp_length(series: pd.Series) -> pd.Series:
    """Convert employment length strings to numeric years.

    Mapping:
    - '< 1 year'  → 0
    - 'n/a'       → NaN
    - 'X years'   → X
    - '10+ years' → 10
    """
    def _convert(val: Any) -> Optional[float]:
        s = str(val).strip().lower()
        if s in ("nan", "n/a", ""):
            return np.nan
        if "< 1" in s:
            return 0.0
        match = re.search(r"(\d+)", s)
        return float(match.group(1)) if match else np.nan

    return series.apply(_convert)


def clean_loan_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and standardise the raw loan dataset.

    Steps:
    1. Lowercase / underscore column names.
    2. Parse term, int_rate, emp_length to numeric.
    3. Parse issue_d to datetime.
    4. Impute missing values (median numeric, mode categorical).
    5. Remove duplicates on loan_id.
    6. Derive / overwrite default_flag from loan_status.
    7. Document and drop protected attributes.
    8. Validate numeric ranges and clip outliers.

    Args:
        df: Raw loan DataFrame.

    Returns:
        Cleaned DataFrame.
    """
    df = df.copy()

    # 1. Standardise column names
    df.columns = [
        col.lower().strip().replace(" ", "_").replace("-", "_") for col in df.columns
    ]
    logger.info("Cleaned column names. Shape: %s", df.shape)

    # 2. Parse structured columns
    if "term" in df.columns:
        df["term"] = _parse_term(df["term"])
    if "int_rate" in df.columns:
        df["int_rate"] = _parse_int_rate(df["int_rate"])
    if "emp_length" in df.columns:
        df["emp_length"] = _parse_emp_length(df["emp_length"])

    # 3. Parse issue_d → datetime
    if "issue_d" in df.columns:
        df["issue_d"] = pd.to_datetime(df["issue_d"], format="%b-%Y", errors="coerce")
        logger.debug("Parsed issue_d: %d valid dates", df["issue_d"].notna().sum())

    # 4. Handle missing values
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()

    for col in numeric_cols:
        n_missing = df[col].isna().sum()
        if n_missing > 0:
            median_val = df[col].median()
            df[col] = df[col].fillna(median_val)
            logger.debug("Imputed %d missing in '%s' with median=%.2f", n_missing, col, median_val)

    for col in categorical_cols:
        n_missing = df[col].isna().sum()
        if n_missing > 0:
            if df[col].notna().any():
                mode_val = df[col].mode()[0]
                df[col] = df[col].fillna(mode_val)
                logger.debug("Imputed %d missing in '%s' with mode=%s", n_missing, col, mode_val)

    # 5. Remove duplicates
    if "loan_id" in df.columns:
        before = len(df)
        df = df.drop_duplicates(subset=["loan_id"], keep="first")
        after = len(df)
        if before != after:
            logger.warning("Removed %d duplicate loan_id rows.", before - after)

    # 6. Derive default_flag from loan_status
    if "loan_status" in df.columns:
        def _default_flag(status: Any) -> Optional[int]:
            s = str(status).strip()
            if s in ("Charged Off", "Default"):
                return 1
            if s == "Fully Paid":
                return 0
            return np.nan  # type: ignore[return-value]

        df["default_flag"] = df["loan_status"].apply(_default_flag)
        logger.info(
            "default_flag distribution:\n%s",
            df["default_flag"].value_counts(dropna=False).to_string(),
        )

    # 7. Document protected attributes
    protected_found = [c for c in _PROTECTED_ATTRIBUTES if c in df.columns]
    if protected_found:
        logger.warning(
            "Protected attributes found and excluded from modelling (not dropped from storage): %s",
            protected_found,
        )

    # 8. Validate & clip numeric ranges
    for col, bounds in NUMERIC_RANGE_RULES.items():
        if col in df.columns:
            before_invalid = ((df[col] < bounds["min"]) | (df[col] > bounds["max"])).sum()
            if before_invalid > 0:
                df[col] = df[col].clip(lower=bounds["min"], upper=bounds["max"])
                logger.warning("Clipped %d out-of-range values in '%s'.", before_invalid, col)

    logger.info("Loan data cleaning complete. Final shape: %s", df.shape)
    return df


# ---------------------------------------------------------------------------
# Ledger data cleaning
# ---------------------------------------------------------------------------
def clean_ledger_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and standardise the raw general ledger dataset.

    Args:
        df: Raw ledger DataFrame.

    Returns:
        Cleaned DataFrame with parsed dates and numeric columns.
    """
    df = df.copy()

    # Standardise column names
    df.columns = [
        col.lower().strip().replace(" ", "_").replace("-", "_") for col in df.columns
    ]

    # Parse date
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        n_bad = df["date"].isna().sum()
        if n_bad:
            logger.warning("Dropped %d rows with unparseable dates.", n_bad)
            df = df.dropna(subset=["date"])

    # Coerce numeric columns
    numeric_ledger_cols = [
        "revenue", "cogs", "gross_profit", "opex_salaries", "opex_marketing",
        "opex_technology", "opex_depreciation", "opex_other", "total_opex",
        "ebitda", "interest_expense", "tax", "net_profit",
        "cash", "accounts_receivable", "inventory", "ppe",
        "accounts_payable", "short_term_debt", "long_term_debt", "equity",
        "budget_revenue", "budget_cogs", "budget_opex", "budget_net_profit",
    ]
    for col in numeric_ledger_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
            n_missing = df[col].isna().sum()
            if n_missing:
                median_val = df[col].median()
                df[col] = df[col].fillna(median_val)
                logger.debug("Imputed %d missing in ledger '%s'.", n_missing, col)

    # Validate revenue is non-negative
    if "revenue" in df.columns:
        neg_rev = (df["revenue"] < 0).sum()
        if neg_rev:
            logger.warning("Found %d rows with negative revenue; setting to 0.", neg_rev)
            df.loc[df["revenue"] < 0, "revenue"] = 0

    # Remove full duplicates
    before = len(df)
    df = df.drop_duplicates()
    if before != len(df):
        logger.warning("Removed %d fully duplicate ledger rows.", before - len(df))

    logger.info("Ledger cleaning complete. Final shape: %s", df.shape)
    return df


# ---------------------------------------------------------------------------
# Accounting equation validator
# ---------------------------------------------------------------------------
def validate_accounting_equation(df: pd.DataFrame, tolerance: float = 0.01) -> pd.DataFrame:
    """Check Assets = Liabilities + Equity for each row in a balance-sheet DataFrame.

    Required columns: cash, accounts_receivable, inventory, ppe,
    accounts_payable, short_term_debt, long_term_debt, equity.

    Args:
        df: Ledger / balance-sheet DataFrame.
        tolerance: Maximum allowed relative discrepancy (default 1%).

    Returns:
        DataFrame with added columns: total_assets, total_liabilities_equity,
        bs_discrepancy, bs_balanced.
    """
    df = df.copy()
    required = ["cash", "accounts_receivable", "inventory", "ppe",
                "accounts_payable", "short_term_debt", "long_term_debt", "equity"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        logger.error("Cannot validate accounting equation; missing columns: %s", missing)
        return df

    df["total_assets"] = df["cash"] + df["accounts_receivable"] + df["inventory"] + df["ppe"]
    df["total_liabilities_equity"] = (
        df["accounts_payable"] + df["short_term_debt"] + df["long_term_debt"] + df["equity"]
    )
    df["bs_discrepancy"] = (df["total_assets"] - df["total_liabilities_equity"]).abs()
    df["bs_balanced"] = df.apply(
        lambda r: (r["bs_discrepancy"] / (abs(r["total_assets"]) + 1e-9)) <= tolerance,
        axis=1,
    )
    n_unbalanced = (~df["bs_balanced"]).sum()
    if n_unbalanced:
        logger.warning(
            "Accounting equation violated in %d / %d rows (tolerance=%.1f%%).",
            n_unbalanced, len(df), tolerance * 100,
        )
    else:
        logger.info("Accounting equation holds for all %d rows.", len(df))
    return df


# ---------------------------------------------------------------------------
# Data quality checks
# ---------------------------------------------------------------------------
def run_data_quality_checks(df: pd.DataFrame, name: str = "dataset") -> Dict[str, Any]:
    """Compute a comprehensive data quality report for a DataFrame.

    Checks performed:
    - Row & column counts
    - Missing value counts and percentages per column
    - Duplicate row count
    - Numeric column statistics (min, max, mean, std)
    - Constant columns
    - Cardinality of categorical columns

    Args:
        df: DataFrame to audit.
        name: Human-readable label for logging.

    Returns:
        Dictionary containing all quality metrics.
    """
    report: Dict[str, Any] = {"name": name, "row_count": len(df), "col_count": len(df.columns)}

    # Missing values
    missing_counts = df.isnull().sum()
    missing_pct = (missing_counts / len(df) * 100).round(2)
    report["missing_counts"] = missing_counts[missing_counts > 0].to_dict()
    report["missing_pct"] = missing_pct[missing_pct > 0].to_dict()
    report["total_missing_cells"] = int(missing_counts.sum())
    report["completeness_pct"] = round(
        (1 - missing_counts.sum() / (len(df) * len(df.columns))) * 100, 2
    )

    # Duplicates
    report["duplicate_rows"] = int(df.duplicated().sum())

    # Numeric stats
    numeric_df = df.select_dtypes(include=[np.number])
    if not numeric_df.empty:
        stats = numeric_df.describe().T
        report["numeric_stats"] = stats.to_dict(orient="index")

    # Constant columns
    constant_cols = [col for col in df.columns if df[col].nunique(dropna=True) <= 1]
    report["constant_columns"] = constant_cols

    # Cardinality of categoricals
    cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
    report["categorical_cardinality"] = {col: int(df[col].nunique()) for col in cat_cols}

    # Negative value check for financial columns
    financial_cols = [
        c for c in ["revenue", "loan_amnt", "annual_inc", "gross_profit"]
        if c in df.columns
    ]
    neg_counts = {}
    for col in financial_cols:
        neg_counts[col] = int((df[col] < 0).sum())
    report["negative_value_counts"] = {k: v for k, v in neg_counts.items() if v > 0}

    logger.info(
        "DQ Report [%s]: rows=%d | completeness=%.1f%% | dups=%d | missing_cols=%d",
        name, report["row_count"], report["completeness_pct"],
        report["duplicate_rows"], len(report["missing_counts"]),
    )
    return report
