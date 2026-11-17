"""
src/data_ingestion.py
=====================
Data ingestion module for the Financial Analytics and Risk Reporting System.

Attempts to load Lending Club data from data/raw/. If not found, generates
realistic synthetic loan and ledger datasets using Faker and numpy.
Saves all raw CSVs to data/raw/ and logs every operation.
"""

import logging
import os
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Tuple

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
GRADES = ["A", "B", "C", "D", "E", "F", "G"]
SUB_GRADES = [f"{g}{n}" for g in GRADES for n in range(1, 6)]
PURPOSES = [
    "debt_consolidation", "credit_card", "home_improvement", "other",
    "major_purchase", "medical", "small_business", "car", "vacation",
    "moving", "house", "wedding", "educational", "renewable_energy",
]
HOME_OWNERSHIP = ["RENT", "OWN", "MORTGAGE", "OTHER"]
LOAN_STATUSES = ["Fully Paid", "Charged Off", "Current", "Default", "Late (31-120 days)"]

REGIONS = ["North", "South", "East", "West", "Central"]
PRODUCTS = ["Personal Loans", "Auto Loans", "Mortgages", "Credit Cards", "Business Loans"]
DEPARTMENTS = ["Sales", "Operations", "Technology", "Finance", "Marketing", "HR", "Risk"]

LOAN_COLUMNS = [
    "loan_id", "id", "loan_amnt", "term", "int_rate", "installment", "grade",
    "sub_grade", "annual_inc", "dti", "emp_length", "home_ownership", "purpose",
    "issue_d", "loan_status", "delinq_2yrs", "revol_bal", "revol_util",
    "inq_last_6mths", "open_acc", "pub_rec", "total_acc", "default_flag",
]


# ---------------------------------------------------------------------------
# Lending Club loader
# ---------------------------------------------------------------------------
def load_lending_club_data(raw_path: Path) -> Optional[pd.DataFrame]:
    """Attempt to load Lending Club loan data from the raw directory.

    Looks for any CSV file containing 'loan' or 'lending' in its name
    (case-insensitive) inside *raw_path*.

    Args:
        raw_path: Path to the data/raw/ directory.

    Returns:
        DataFrame if a file is found and loaded, else None.
    """
    raw_path = Path(raw_path)
    candidates = [
        f for pattern in ("*.csv", "*.csv.gz")
        for f in raw_path.glob(pattern)
        if "rejected" not in f.name.lower()
        and any(kw in f.name.lower() for kw in ("accepted", "loan", "lending", "lc_"))
    ]
    if not candidates:
        logger.info("No Lending Club CSV found in %s — will generate synthetic data.", raw_path)
        return None

    # Prefer the original accepted-loans export over a previously generated copy.
    path = sorted(
        candidates,
        key=lambda f: (
            0 if f.name.lower().startswith("accepted_") else 1,
            0 if f.name.lower() != "loans_raw.csv" else 1,
            f.name,
        ),
    )[0]
    logger.info("Loading Lending Club data from %s", path)
    try:
        header = pd.read_csv(path, nrows=0)
        normalized_headers = {
            col.lower().strip().replace(" ", "_").replace("-", "_"): col
            for col in header.columns
        }
        source_columns = [
            normalized_headers[column]
            for column in LOAN_COLUMNS
            if column in normalized_headers
        ]
        df = pd.read_csv(
            path,
            usecols=source_columns or None,
            low_memory=False,
        )
        df.columns = [
            col.lower().strip().replace(" ", "_").replace("-", "_")
            for col in df.columns
        ]
        if "loan_id" not in df.columns and "id" in df.columns:
            df = df.rename(columns={"id": "loan_id"})
        logger.info("Loaded %d rows × %d cols from %s", len(df), len(df.columns), path.name)
        return df
    except Exception as exc:  # noqa: BLE001
        logger.error("Failed to load %s: %s", path, exc)
        return None


# ---------------------------------------------------------------------------
# Synthetic loan data generator
# ---------------------------------------------------------------------------
def generate_synthetic_loans(
    n_records: int = 10_000,
    random_state: int = 42,
) -> pd.DataFrame:
    """Generate a synthetic loan dataset with realistic distributions.

    The dataset mimics Lending Club structure with:
    - Realistic grade-to-interest-rate mapping
    - Seasonality in issue dates (more loans in Q4)
    - Grade-correlated default probabilities
    - Realistic DTI, income, and revolving utilization distributions

    Args:
        n_records: Number of loan records to generate.
        random_state: Seed for reproducibility.

    Returns:
        DataFrame with 22 columns matching the Lending Club schema plus
        ``default_flag``.
    """
    rng = np.random.default_rng(random_state)
    random.seed(random_state)

    logger.info("Generating %d synthetic loan records (seed=%d)…", n_records, random_state)

    # --- Grade weights: A=most common, G=rare ---
    grade_weights = [0.22, 0.25, 0.22, 0.15, 0.09, 0.05, 0.02]
    grades = rng.choice(GRADES, size=n_records, p=grade_weights)

    # --- Grade → base interest rate ---
    grade_int_rate_mean = {"A": 7.5, "B": 11.0, "C": 14.5, "D": 17.5, "E": 20.5, "F": 24.0, "G": 27.0}
    int_rates = np.array([
        max(5.0, min(36.0, grade_int_rate_mean[g] + rng.normal(0, 1.5)))
        for g in grades
    ])

    # --- Sub-grade ---
    sub_grades = [
        f"{g}{rng.integers(1, 6)}" for g in grades
    ]

    # --- Loan amount: log-normal, range $1k–$40k ---
    loan_amnt = np.round(
        np.clip(rng.lognormal(mean=9.0, sigma=0.6, size=n_records), 1_000, 40_000), -2
    )

    # --- Term: 36 or 60 months ---
    term_weights = [0.72, 0.28]
    terms = rng.choice([36, 60], size=n_records, p=term_weights)

    # --- Installment ---
    monthly_rate = int_rates / 100 / 12
    installments = np.where(
        monthly_rate == 0,
        loan_amnt / terms,
        loan_amnt * monthly_rate / (1 - (1 + monthly_rate) ** (-terms)),
    )
    installments = np.round(installments, 2)

    # --- Annual income: log-normal ---
    annual_inc = np.round(
        np.clip(rng.lognormal(mean=10.9, sigma=0.55, size=n_records), 15_000, 500_000), -2
    )

    # --- DTI: correlated with grade ---
    grade_dti_mean = {"A": 12, "B": 16, "C": 20, "D": 23, "E": 26, "F": 29, "G": 32}
    dtis = np.clip(
        np.array([grade_dti_mean[g] for g in grades]) + rng.normal(0, 5, n_records), 0, 45
    ).round(2)

    # --- Employment length ---
    emp_length_opts = ["< 1 year", "1 year", "2 years", "3 years", "4 years",
                       "5 years", "6 years", "7 years", "8 years", "9 years", "10+ years", "n/a"]
    emp_length_weights = [0.08, 0.08, 0.09, 0.09, 0.08, 0.09, 0.08, 0.07, 0.07, 0.06, 0.18, 0.03]
    emp_lengths = rng.choice(emp_length_opts, size=n_records, p=emp_length_weights)

    # --- Home ownership ---
    home_own_weights = [0.50, 0.12, 0.35, 0.03]
    home_ownerships = rng.choice(HOME_OWNERSHIP, size=n_records, p=home_own_weights)

    # --- Purpose ---
    purpose_weights = [0.35, 0.18, 0.12, 0.08, 0.06, 0.04, 0.04, 0.04, 0.03, 0.02, 0.01, 0.01, 0.01, 0.01]
    purposes = rng.choice(PURPOSES, size=n_records, p=purpose_weights)

    # --- Issue date: 2022-01-01 to 2024-06-30 with Q4 spike ---
    start_dt = datetime(2022, 1, 1)
    end_dt = datetime(2024, 6, 30)
    total_days = (end_dt - start_dt).days
    raw_days = rng.integers(0, total_days, size=n_records)
    issue_dates = [start_dt + timedelta(days=int(d)) for d in raw_days]
    # Increase Q4 representation
    q4_boost_indices = rng.choice(n_records, size=n_records // 5, replace=False)
    for idx in q4_boost_indices:
        year = rng.choice([2022, 2023])
        month = rng.integers(10, 13)
        day = rng.integers(1, 29)
        issue_dates[idx] = datetime(year, month, day)
    issue_d_strs = [d.strftime("%b-%Y") for d in issue_dates]

    # --- Loan status (grade-correlated) ---
    grade_default_prob = {"A": 0.05, "B": 0.10, "C": 0.17, "D": 0.26, "E": 0.35, "F": 0.46, "G": 0.55}
    default_probs = np.array([grade_default_prob[g] for g in grades])
    rand_vals = rng.random(n_records)
    loan_statuses = []
    default_flags = []
    for prob, rv in zip(default_probs, rand_vals):
        if rv < prob * 0.7:
            loan_statuses.append("Charged Off")
            default_flags.append(1)
        elif rv < prob:
            loan_statuses.append("Default")
            default_flags.append(1)
        elif rv < prob + 0.3:
            loan_statuses.append("Fully Paid")
            default_flags.append(0)
        elif rv < prob + 0.55:
            loan_statuses.append("Current")
            default_flags.append(0)
        else:
            loan_statuses.append("Late (31-120 days)")
            default_flags.append(0)

    # --- Delinquencies in last 2 years ---
    delinq_2yrs = rng.choice([0, 1, 2, 3, 4, 5], size=n_records,
                              p=[0.60, 0.20, 0.10, 0.05, 0.03, 0.02])

    # --- Revolving balance & utilization ---
    revol_bal = np.round(
        np.clip(rng.lognormal(mean=8.5, sigma=0.9, size=n_records), 0, 150_000), 2
    )
    revol_util = np.clip(
        np.array([grade_dti_mean[g] for g in grades]) * 1.5 + rng.normal(0, 15, n_records),
        0, 100,
    ).round(1)

    # --- Inquiries last 6 months ---
    inq_last_6mths = rng.choice([0, 1, 2, 3, 4, 5, 6], size=n_records,
                                 p=[0.40, 0.25, 0.15, 0.09, 0.05, 0.04, 0.02])

    # --- Open accounts ---
    open_acc = rng.integers(2, 30, size=n_records)

    # --- Public records ---
    pub_rec = rng.choice([0, 1, 2, 3], size=n_records, p=[0.80, 0.14, 0.04, 0.02])

    # --- Total accounts ---
    total_acc = open_acc + rng.integers(0, 20, size=n_records)

    # --- Loan IDs ---
    loan_ids = [f"LC{str(i).zfill(7)}" for i in range(1, n_records + 1)]

    df = pd.DataFrame({
        "loan_id": loan_ids,
        "loan_amnt": loan_amnt,
        "term": [f"{t} months" for t in terms],
        "int_rate": [f"{r:.2f}%" for r in int_rates],
        "installment": installments,
        "grade": grades,
        "sub_grade": sub_grades,
        "annual_inc": annual_inc,
        "dti": dtis,
        "emp_length": emp_lengths,
        "home_ownership": home_ownerships,
        "purpose": purposes,
        "issue_d": issue_d_strs,
        "loan_status": loan_statuses,
        "delinq_2yrs": delinq_2yrs,
        "revol_bal": revol_bal,
        "revol_util": revol_util,
        "inq_last_6mths": inq_last_6mths,
        "open_acc": open_acc,
        "pub_rec": pub_rec,
        "total_acc": total_acc,
        "default_flag": default_flags,
    })

    logger.info(
        "Synthetic loan data: %d rows | default rate=%.1f%%",
        len(df),
        df["default_flag"].mean() * 100,
    )
    return df


# ---------------------------------------------------------------------------
# Synthetic ledger generator
# ---------------------------------------------------------------------------
def generate_synthetic_ledger(
    n_months: int = 24,
    start_date: str = "2024-01-01",
    regions: Optional[list] = None,
    products: Optional[list] = None,
    departments: Optional[list] = None,
    random_state: int = 42,
) -> pd.DataFrame:
    """Generate a synthetic monthly general ledger dataset.

    Features:
    - Revenue peaks in Q4 (seasonality factor)
    - Intentional budget variances (mostly ±5–10%)
    - One anomaly month with a large marketing spend spike
    - Realistic COGS (35–40% of revenue)
    - OPEX components follow realistic proportions

    Args:
        n_months: Number of months to generate.
        start_date: First month in YYYY-MM-DD format.
        regions: List of region names.
        products: List of product names.
        departments: List of department names.
        random_state: Seed for reproducibility.

    Returns:
        DataFrame with ~31 financial columns per (date, region, product, department).
    """
    rng = np.random.default_rng(random_state)
    regions = regions or REGIONS
    products = products or PRODUCTS
    departments = departments or DEPARTMENTS

    start_dt = pd.Timestamp(start_date)
    dates = [start_dt + pd.DateOffset(months=m) for m in range(n_months)]

    # Anomaly month: month 7 (index 6) has marketing spike
    anomaly_month_idx = 6

    rows = []
    for date_idx, date in enumerate(dates):
        month = date.month
        # Seasonality: Q4 boost, Q1 slight dip
        seasonality = {
            1: 0.88, 2: 0.90, 3: 0.95, 4: 1.00, 5: 1.02, 6: 1.04,
            7: 1.06, 8: 1.05, 9: 1.08, 10: 1.12, 11: 1.18, 12: 1.25,
        }[month]

        for region in regions:
            region_factor = {
                "North": 1.10, "South": 0.95, "East": 1.05, "West": 1.08, "Central": 0.90,
            }.get(region, 1.0)

            for product in products:
                product_factor = {
                    "Personal Loans": 1.00, "Auto Loans": 0.90, "Mortgages": 1.40,
                    "Credit Cards": 0.75, "Business Loans": 1.20,
                }.get(product, 1.0)

                for dept in departments:
                    base_revenue = 500_000 * seasonality * region_factor * product_factor
                    revenue = base_revenue * (1 + rng.normal(0, 0.04))

                    cogs_pct = 0.37 + rng.uniform(-0.03, 0.03)
                    cogs = revenue * cogs_pct
                    gross_profit = revenue - cogs

                    # OPEX components
                    opex_salaries = revenue * (0.18 + rng.uniform(-0.02, 0.02))
                    is_anomaly = (date_idx == anomaly_month_idx and dept == "Marketing")
                    marketing_base = revenue * (0.06 + rng.uniform(-0.01, 0.01))
                    opex_marketing = marketing_base * 3.5 if is_anomaly else marketing_base
                    opex_technology = revenue * (0.07 + rng.uniform(-0.01, 0.01))
                    opex_depreciation = revenue * (0.025 + rng.uniform(-0.005, 0.005))
                    opex_other = revenue * (0.03 + rng.uniform(-0.01, 0.01))
                    total_opex = opex_salaries + opex_marketing + opex_technology + opex_depreciation + opex_other

                    ebitda = gross_profit - total_opex + opex_depreciation
                    interest_expense = revenue * (0.03 + rng.uniform(-0.005, 0.005))
                    tax_rate = 0.21 + rng.uniform(-0.02, 0.02)
                    ebit = ebitda - opex_depreciation
                    pbt = ebit - interest_expense
                    tax = max(0, pbt * tax_rate)
                    net_profit = pbt - tax

                    # Balance sheet components
                    cash = revenue * (0.15 + rng.uniform(-0.03, 0.03))
                    accounts_receivable = revenue * (0.20 + rng.uniform(-0.03, 0.03))
                    inventory = revenue * (0.05 + rng.uniform(-0.01, 0.01))
                    ppe = revenue * 2.5 + rng.uniform(-50_000, 50_000)
                    accounts_payable = cogs * (0.25 + rng.uniform(-0.03, 0.03))
                    short_term_debt = revenue * (0.10 + rng.uniform(-0.02, 0.02))
                    long_term_debt = revenue * 1.8 + rng.uniform(-100_000, 100_000)
                    equity = (cash + accounts_receivable + inventory + ppe) - (accounts_payable + short_term_debt + long_term_debt)

                    # Budget figures (intentionally off by ±3–12%)
                    budget_variance_factor_rev = 1 + rng.uniform(-0.08, 0.05)
                    budget_variance_factor_cogs = 1 + rng.uniform(-0.05, 0.08)
                    budget_variance_factor_opex = 1 + rng.uniform(-0.06, 0.10)
                    budget_revenue = revenue / budget_variance_factor_rev
                    budget_cogs = cogs / budget_variance_factor_cogs
                    budget_opex = total_opex / budget_variance_factor_opex
                    budget_net_profit = budget_revenue - budget_cogs - budget_opex - interest_expense - (max(0, (budget_revenue - budget_cogs - budget_opex - interest_expense)) * tax_rate)

                    rows.append({
                        "date": date.strftime("%Y-%m-%d"),
                        "region": region,
                        "product": product,
                        "department": dept,
                        "revenue": round(revenue, 2),
                        "cogs": round(cogs, 2),
                        "gross_profit": round(gross_profit, 2),
                        "opex_salaries": round(opex_salaries, 2),
                        "opex_marketing": round(opex_marketing, 2),
                        "opex_technology": round(opex_technology, 2),
                        "opex_depreciation": round(opex_depreciation, 2),
                        "opex_other": round(opex_other, 2),
                        "total_opex": round(total_opex, 2),
                        "ebitda": round(ebitda, 2),
                        "interest_expense": round(interest_expense, 2),
                        "tax": round(tax, 2),
                        "net_profit": round(net_profit, 2),
                        "cash": round(cash, 2),
                        "accounts_receivable": round(accounts_receivable, 2),
                        "inventory": round(inventory, 2),
                        "ppe": round(ppe, 2),
                        "accounts_payable": round(accounts_payable, 2),
                        "short_term_debt": round(short_term_debt, 2),
                        "long_term_debt": round(long_term_debt, 2),
                        "equity": round(equity, 2),
                        "budget_revenue": round(budget_revenue, 2),
                        "budget_cogs": round(budget_cogs, 2),
                        "budget_opex": round(budget_opex, 2),
                        "budget_net_profit": round(budget_net_profit, 2),
                    })

    df = pd.DataFrame(rows)
    logger.info(
        "Synthetic ledger: %d rows | date range %s → %s",
        len(df), df["date"].min(), df["date"].max(),
    )
    return df


# ---------------------------------------------------------------------------
# Save helpers
# ---------------------------------------------------------------------------
def save_raw_data(
    loans_df: pd.DataFrame,
    ledger_df: pd.DataFrame,
    raw_path: Path,
) -> Tuple[Path, Path]:
    """Persist raw DataFrames as CSV files.

    Args:
        loans_df: Loan dataset DataFrame.
        ledger_df: Ledger dataset DataFrame.
        raw_path: Directory in which to save the CSVs.

    Returns:
        Tuple of (loans_csv_path, ledger_csv_path).
    """
    raw_path = Path(raw_path)
    raw_path.mkdir(parents=True, exist_ok=True)

    loans_path = raw_path / "loans_raw.csv"
    ledger_path = raw_path / "ledger_raw.csv"

    loans_df.to_csv(loans_path, index=False)
    logger.info("Saved loan data → %s (%d rows)", loans_path, len(loans_df))

    ledger_df.to_csv(ledger_path, index=False)
    logger.info("Saved ledger data → %s (%d rows)", ledger_path, len(ledger_df))

    return loans_path, ledger_path


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------
def ingest_data(
    raw_path: Optional[Path] = None,
    n_loan_records: int = 10_000,
    n_months: int = 24,
    start_date: str = "2024-01-01",
    regions: Optional[list] = None,
    products: Optional[list] = None,
    departments: Optional[list] = None,
    random_state: int = 42,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Orchestrate data ingestion: load or generate, then save.

    Tries to load a Lending Club CSV from *raw_path* first.
    Falls back to synthetic data if none is found.

    Args:
        raw_path: Path to data/raw/ directory. Defaults to PROJECT_ROOT/data/raw.
        n_loan_records: Number of synthetic loan records if generation is required.
        n_months: Number of ledger months to generate.
        start_date: First month for ledger generation.
        regions: Region list for ledger.
        products: Product list for ledger.
        departments: Department list for ledger.
        random_state: RNG seed.

    Returns:
        Tuple of (loans_df, ledger_df) as raw DataFrames.
    """
    from src.config import get_data_path  # local import to avoid circular deps at module load

    if raw_path is None:
        try:
            raw_path = get_data_path("raw")
        except Exception:
            raw_path = Path("data/raw")

    raw_path = Path(raw_path)

    # Loans
    loans_df = load_lending_club_data(raw_path)
    if loans_df is None:
        loans_df = generate_synthetic_loans(
            n_records=n_loan_records, random_state=random_state
        )
    else:
        # Ensure default_flag exists even on real LC data. Unresolved statuses
        # remain unknown and are excluded from scorecard training downstream.
        if "default_flag" not in loans_df.columns and "loan_status" in loans_df.columns:
            status = loans_df["loan_status"].astype(str).str.strip().str.lower()
            loans_df["default_flag"] = np.select(
                [status.isin({"charged off", "default"}), status.str.contains("fully paid", na=False)],
                [1, 0],
                default=np.nan,
            )

    # Ledger
    ledger_csv = raw_path / "ledger_raw.csv"
    if ledger_csv.exists():
        ledger_df = pd.read_csv(ledger_csv)
        logger.info("Loaded existing ledger from %s", ledger_csv)
    else:
        ledger_df = generate_synthetic_ledger(
            n_months=n_months,
            start_date=start_date,
            regions=regions,
            products=products,
            departments=departments,
            random_state=random_state,
        )

    save_raw_data(loans_df, ledger_df, raw_path)
    return loans_df, ledger_df


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    loans, ledger = ingest_data()
    print(f"Loans shape : {loans.shape}")
    print(f"Ledger shape: {ledger.shape}")
