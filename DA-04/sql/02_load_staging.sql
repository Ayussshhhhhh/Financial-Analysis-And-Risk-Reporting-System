-- ============================================================================
-- 02_load_staging.sql
-- Financial Analytics and Risk Reporting System
-- Staging data preparation and schema validation transformations
-- ============================================================================

-- Staging table for Loan Originations and Applications
DROP TABLE IF EXISTS stg_loans;
CREATE TABLE stg_loans (
    loan_id VARCHAR(50),
    loan_amnt NUMERIC(15, 2),
    term INT,
    int_rate NUMERIC(6, 4),
    installment NUMERIC(10, 2),
    grade VARCHAR(2),
    sub_grade VARCHAR(4),
    annual_inc NUMERIC(15, 2),
    dti NUMERIC(6, 2),
    emp_length INT,
    home_ownership VARCHAR(20),
    purpose VARCHAR(50),
    issue_d DATE,
    loan_status VARCHAR(50),
    delinq_2yrs INT,
    revol_bal NUMERIC(15, 2),
    revol_util NUMERIC(6, 2),
    inq_last_6mths INT,
    open_acc INT,
    pub_rec INT,
    total_acc INT,
    default_flag INT
);

-- Staging table for Monthly General Ledger Transactions & Balances
DROP TABLE IF EXISTS stg_ledger;
CREATE TABLE stg_ledger (
    transaction_date DATE,
    region VARCHAR(50),
    product VARCHAR(100),
    department VARCHAR(100),
    revenue NUMERIC(15, 2),
    cogs NUMERIC(15, 2),
    gross_profit NUMERIC(15, 2),
    opex_salaries NUMERIC(15, 2),
    opex_marketing NUMERIC(15, 2),
    opex_technology NUMERIC(15, 2),
    opex_depreciation NUMERIC(15, 2),
    opex_other NUMERIC(15, 2),
    total_opex NUMERIC(15, 2),
    ebitda NUMERIC(15, 2),
    ebit NUMERIC(15, 2),
    interest_expense NUMERIC(15, 2),
    tax NUMERIC(15, 2),
    net_profit NUMERIC(15, 2),
    cash NUMERIC(15, 2),
    accounts_receivable NUMERIC(15, 2),
    inventory NUMERIC(15, 2),
    ppe NUMERIC(15, 2),
    total_assets NUMERIC(15, 2),
    accounts_payable NUMERIC(15, 2),
    short_term_debt NUMERIC(15, 2),
    long_term_debt NUMERIC(15, 2),
    equity NUMERIC(15, 2),
    total_liabilities_equity NUMERIC(15, 2),
    budget_revenue NUMERIC(15, 2),
    budget_cogs NUMERIC(15, 2),
    budget_opex NUMERIC(15, 2),
    budget_net_profit NUMERIC(15, 2)
);
