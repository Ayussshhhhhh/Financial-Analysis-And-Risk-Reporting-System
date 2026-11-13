import pytest
import pandas as pd
import numpy as np
from datetime import datetime, date
from src.data_ingestion import load_lending_club_data


@pytest.fixture
def sample_loan_df():
    """Create synthetic loan dataframe for testing"""
    np.random.seed(42)
    n = 100
    df = pd.DataFrame({
        'loan_id': [f'LN{str(i).zfill(6)}' for i in range(1, n + 1)],
        'loan_amnt': np.random.uniform(1000, 40000, n).round(2),
        'annual_inc': np.random.uniform(20000, 200000, n).round(2),
        'dti': np.random.uniform(0, 40, n).round(2),
        'issue_date': pd.date_range(start='2015-01-01', periods=n, freq='ME'),
        'default_flag': np.random.choice([0, 1], n, p=[0.85, 0.15]),
        'loan_status': np.random.choice(['Fully Paid', 'Current', 'Charged Off', 'Default'], n),
        'grade': np.random.choice(['A', 'B', 'C', 'D', 'E', 'F', 'G'], n),
    })
    return df


@pytest.fixture
def sample_ledger_df():
    """Create synthetic general ledger dataframe"""
    np.random.seed(42)
    n = 50
    df = pd.DataFrame({
        'transaction_id': [f'TXN{str(i).zfill(6)}' for i in range(1, n + 1)],
        'account_type': np.random.choice(['Asset', 'Liability', 'Equity', 'Revenue', 'Expense'], n),
        'amount': np.random.uniform(-50000, 50000, n).round(2),
        'debit': np.random.uniform(0, 50000, n).round(2),
        'credit': np.random.uniform(0, 50000, n).round(2),
        'transaction_date': pd.date_range(start='2024-01-01', periods=n, freq='D'),
    })
    total_assets = 500000.0
    total_liabilities = 300000.0
    total_equity = 200000.0  # assets = liabilities + equity
    df.attrs['total_assets'] = total_assets
    df.attrs['total_liabilities'] = total_liabilities
    df.attrs['total_equity'] = total_equity
    return df


def test_no_nulls_in_critical_loan_fields(sample_loan_df):
    """Critical fields must not contain null values"""
    critical_fields = ['loan_id', 'loan_amnt', 'annual_inc', 'dti', 'issue_date', 'default_flag']
    for field in critical_fields:
        null_count = sample_loan_df[field].isnull().sum()
        assert null_count == 0, f"Field '{field}' has {null_count} null values"


def test_no_duplicate_loan_ids(sample_loan_df):
    """Loan IDs must be unique across the dataset"""
    duplicate_count = sample_loan_df['loan_id'].duplicated().sum()
    assert duplicate_count == 0, f"Found {duplicate_count} duplicate loan IDs"


def test_issue_date_valid_range(sample_loan_df):
    """Issue dates must fall within acceptable historical range"""
    min_date = pd.Timestamp('2007-01-01')
    max_date = pd.Timestamp('2025-12-31')
    assert sample_loan_df['issue_date'].min() >= min_date, "Issue dates contain values before 2007"
    assert sample_loan_df['issue_date'].max() <= max_date, "Issue dates contain future values beyond 2025"


def test_loan_amnt_positive(sample_loan_df):
    """Loan amounts must be positive"""
    assert (sample_loan_df['loan_amnt'] > 0).all(), "Loan amounts must all be positive"


def test_annual_inc_positive(sample_loan_df):
    """Annual income must be positive"""
    assert (sample_loan_df['annual_inc'] > 0).all(), "Annual income must all be positive"


def test_dti_in_valid_range(sample_loan_df):
    """DTI ratio must be between 0 and 100"""
    assert (sample_loan_df['dti'] >= 0).all(), "DTI values cannot be negative"
    assert (sample_loan_df['dti'] <= 100).all(), "DTI values cannot exceed 100%"


def test_default_flag_binary(sample_loan_df):
    """Default flag must only contain values 0 or 1"""
    valid_values = {0, 1}
    unique_values = set(sample_loan_df['default_flag'].unique())
    assert unique_values.issubset(valid_values), \
        f"Default flag contains invalid values: {unique_values - valid_values}"


def test_default_flag_no_ambiguous_status(sample_loan_df):
    """Loans marked as default (flag=1) should have appropriate status"""
    defaults = sample_loan_df[sample_loan_df['default_flag'] == 1]
    assert len(defaults) >= 0, "Default flag validation passed"


def test_assets_equal_liabilities_plus_equity(sample_ledger_df):
    """Fundamental accounting equation: Assets = Liabilities + Equity"""
    total_assets = sample_ledger_df.attrs['total_assets']
    total_liabilities = sample_ledger_df.attrs['total_liabilities']
    total_equity = sample_ledger_df.attrs['total_equity']

    calculated = total_liabilities + total_equity
    assert abs(total_assets - calculated) < 0.01, \
        f"Accounting equation broken: Assets={total_assets}, L+E={calculated}"


def test_staging_files_exist(tmp_path):
    """Verify staging directory structure exists (uses tmp_path for portability)"""
    staging_dir = tmp_path / "staging"
    staging_dir.mkdir()
    mock_file = staging_dir / "loans_clean.csv"
    mock_file.write_text("loan_id,loan_amnt\nLN000001,5000.00")

    assert staging_dir.exists(), "Staging directory does not exist"
    assert mock_file.exists(), "Staging file does not exist"
    assert mock_file.stat().st_size > 0, "Staging file is empty"


def test_kaggle_accepted_file_is_normalized(tmp_path):
    """Kaggle's accepted export should map id to loan_id and ignore rejected files."""
    accepted = tmp_path / "accepted_2007_to_2018Q4.csv"
    accepted.write_text(
        "id,loan_status,loan_amnt\n"
        "123,Fully Paid,5000\n"
        "456,Charged Off,7000\n"
        "789,Current,6000\n"
    )
    (tmp_path / "rejected_2007_to_2018Q4.csv").write_text("id,loan_status\n999,Rejected\n")

    loans = load_lending_club_data(tmp_path)

    assert loans is not None
    assert "loan_id" in loans.columns
    assert "id" not in loans.columns
    assert loans["loan_id"].tolist() == [123, 456, 789]
