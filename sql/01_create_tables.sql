-- ============================================================================
-- 01_create_tables.sql
-- Financial Analytics and Risk Reporting System
-- Analytical Star Schema DDL for SQLite / PostgreSQL compatible SQL
-- ============================================================================

-- Drop tables if existing for idempotent runs
DROP TABLE IF EXISTS fact_loan_performance;
DROP TABLE IF EXISTS fact_general_ledger;
DROP TABLE IF EXISTS fact_budget_actual;
DROP TABLE IF EXISTS fact_balance_sheet;
DROP TABLE IF EXISTS fact_credit_application;
DROP TABLE IF EXISTS dim_date;
DROP TABLE IF EXISTS dim_customer;
DROP TABLE IF EXISTS dim_loan;
DROP TABLE IF EXISTS dim_product;
DROP TABLE IF EXISTS dim_risk_band;
DROP TABLE IF EXISTS dim_account;
DROP TABLE IF EXISTS dim_department;
DROP TABLE IF EXISTS dim_region;

-- ----------------------------------------------------------------------------
-- Dimension Tables
-- ----------------------------------------------------------------------------

-- 1. Date Dimension
CREATE TABLE dim_date (
    date_key INT PRIMARY KEY,
    full_date DATE NOT NULL,
    year INT NOT NULL,
    quarter INT NOT NULL,
    month INT NOT NULL,
    month_name VARCHAR(20) NOT NULL,
    week INT NOT NULL,
    day INT NOT NULL,
    is_weekend INT NOT NULL,
    is_month_end INT NOT NULL,
    fiscal_year INT NOT NULL,
    fiscal_quarter INT NOT NULL
);

-- 2. Region Dimension
CREATE TABLE dim_region (
    region_id INT PRIMARY KEY,
    region_name VARCHAR(50) NOT NULL,
    region_code VARCHAR(10) NOT NULL,
    country VARCHAR(50) DEFAULT 'United States'
);

-- 3. Department Dimension
CREATE TABLE dim_department (
    dept_id INT PRIMARY KEY,
    dept_name VARCHAR(100) NOT NULL,
    dept_code VARCHAR(20) NOT NULL,
    cost_center VARCHAR(20) NOT NULL,
    region_id INT,
    FOREIGN KEY (region_id) REFERENCES dim_region(region_id)
);

-- 4. Product Dimension
CREATE TABLE dim_product (
    product_id INT PRIMARY KEY,
    product_name VARCHAR(100) NOT NULL,
    product_category VARCHAR(50) NOT NULL,
    interest_type VARCHAR(20) DEFAULT 'Fixed',
    term_months INT NOT NULL
);

-- 5. Risk Band Dimension
CREATE TABLE dim_risk_band (
    risk_band_id INT PRIMARY KEY,
    risk_band_name VARCHAR(50) NOT NULL,
    min_score NUMERIC(6, 2) NOT NULL,
    max_score NUMERIC(6, 2) NOT NULL,
    expected_pd_low NUMERIC(6, 4) NOT NULL,
    expected_pd_high NUMERIC(6, 4) NOT NULL,
    color_code VARCHAR(10) NOT NULL
);

-- 6. Customer Dimension
CREATE TABLE dim_customer (
    customer_id VARCHAR(50) PRIMARY KEY,
    home_ownership VARCHAR(20),
    annual_income NUMERIC(15, 2),
    income_bucket VARCHAR(30),
    dti NUMERIC(6, 2),
    dti_bucket VARCHAR(30),
    emp_length_years INT,
    region_id INT,
    FOREIGN KEY (region_id) REFERENCES dim_region(region_id)
);

-- 7. Loan Dimension
CREATE TABLE dim_loan (
    loan_id VARCHAR(50) PRIMARY KEY,
    loan_amnt NUMERIC(15, 2) NOT NULL,
    term INT NOT NULL,
    int_rate NUMERIC(6, 4) NOT NULL,
    installment NUMERIC(10, 2) NOT NULL,
    grade VARCHAR(2) NOT NULL,
    sub_grade VARCHAR(4) NOT NULL,
    purpose VARCHAR(50) NOT NULL,
    issue_date DATE NOT NULL
);

-- 8. Account Dimension (General Ledger Chart of Accounts)
CREATE TABLE dim_account (
    account_id INT PRIMARY KEY,
    account_name VARCHAR(100) NOT NULL,
    account_type VARCHAR(50) NOT NULL, -- Asset, Liability, Equity, Revenue, Expense
    account_category VARCHAR(50) NOT NULL,
    parent_account INT
);

-- ----------------------------------------------------------------------------
-- Fact Tables
-- ----------------------------------------------------------------------------

-- 1. General Ledger Fact Table
CREATE TABLE fact_general_ledger (
    gl_id INT PRIMARY KEY,
    date_key INT NOT NULL,
    account_id INT NOT NULL,
    dept_id INT,
    region_id INT,
    product_id INT,
    actual_amount NUMERIC(15, 2) NOT NULL,
    budget_amount NUMERIC(15, 2),
    variance NUMERIC(15, 2),
    is_favorable INT,
    FOREIGN KEY (date_key) REFERENCES dim_date(date_key),
    FOREIGN KEY (account_id) REFERENCES dim_account(account_id),
    FOREIGN KEY (dept_id) REFERENCES dim_department(dept_id),
    FOREIGN KEY (region_id) REFERENCES dim_region(region_id),
    FOREIGN KEY (product_id) REFERENCES dim_product(product_id)
);

-- 2. Budget vs. Actual Fact Table
CREATE TABLE fact_budget_actual (
    id INT PRIMARY KEY,
    date_key INT NOT NULL,
    dept_id INT,
    region_id INT,
    product_id INT,
    metric_name VARCHAR(100) NOT NULL,
    actual_value NUMERIC(15, 2) NOT NULL,
    budget_value NUMERIC(15, 2) NOT NULL,
    prior_year_value NUMERIC(15, 2),
    variance NUMERIC(15, 2) NOT NULL,
    variance_pct NUMERIC(8, 4) NOT NULL,
    is_favorable INT NOT NULL,
    FOREIGN KEY (date_key) REFERENCES dim_date(date_key),
    FOREIGN KEY (dept_id) REFERENCES dim_department(dept_id),
    FOREIGN KEY (region_id) REFERENCES dim_region(region_id),
    FOREIGN KEY (product_id) REFERENCES dim_product(product_id)
);

-- 3. Balance Sheet Fact Table
CREATE TABLE fact_balance_sheet (
    bs_id INT PRIMARY KEY,
    date_key INT NOT NULL,
    cash NUMERIC(15, 2) NOT NULL,
    accounts_receivable NUMERIC(15, 2) NOT NULL,
    inventory NUMERIC(15, 2) NOT NULL,
    ppe NUMERIC(15, 2) NOT NULL,
    total_assets NUMERIC(15, 2) NOT NULL,
    accounts_payable NUMERIC(15, 2) NOT NULL,
    short_term_debt NUMERIC(15, 2) NOT NULL,
    long_term_debt NUMERIC(15, 2) NOT NULL,
    equity NUMERIC(15, 2) NOT NULL,
    total_liabilities_equity NUMERIC(15, 2) NOT NULL,
    is_balanced INT NOT NULL,
    FOREIGN KEY (date_key) REFERENCES dim_date(date_key)
);

-- 4. Credit Application Fact Table
CREATE TABLE fact_credit_application (
    app_id VARCHAR(50) PRIMARY KEY,
    date_key INT NOT NULL,
    customer_id VARCHAR(50) NOT NULL,
    loan_id VARCHAR(50) NOT NULL,
    loan_amnt NUMERIC(15, 2) NOT NULL,
    annual_inc NUMERIC(15, 2) NOT NULL,
    dti NUMERIC(6, 2) NOT NULL,
    int_rate NUMERIC(6, 4) NOT NULL,
    term INT NOT NULL,
    grade VARCHAR(2) NOT NULL,
    scorecard_points NUMERIC(6, 1) NOT NULL,
    risk_band_id INT NOT NULL,
    default_flag INT,
    pd_estimate NUMERIC(6, 4) NOT NULL,
    FOREIGN KEY (date_key) REFERENCES dim_date(date_key),
    FOREIGN KEY (customer_id) REFERENCES dim_customer(customer_id),
    FOREIGN KEY (loan_id) REFERENCES dim_loan(loan_id),
    FOREIGN KEY (risk_band_id) REFERENCES dim_risk_band(risk_band_id)
);

-- 5. Loan Performance & Risk Fact Table
CREATE TABLE fact_loan_performance (
    loan_id VARCHAR(50) PRIMARY KEY,
    customer_id VARCHAR(50),
    product_id INT,
    risk_band_id INT,
    loan_status VARCHAR(50) NOT NULL,
    default_flag INT,
    pd_score NUMERIC(6, 4) NOT NULL,
    scorecard_points NUMERIC(6, 1) NOT NULL,
    expected_loss NUMERIC(15, 2) NOT NULL,
    lgd_assumption NUMERIC(6, 4) DEFAULT 0.4500,
    ead NUMERIC(15, 2) NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES dim_customer(customer_id),
    FOREIGN KEY (product_id) REFERENCES dim_product(product_id),
    FOREIGN KEY (risk_band_id) REFERENCES dim_risk_band(risk_band_id)
);

-- Performance Indexes
CREATE INDEX idx_gl_date ON fact_general_ledger(date_key);
CREATE INDEX idx_bgt_date ON fact_budget_actual(date_key);
CREATE INDEX idx_loan_risk ON fact_loan_performance(risk_band_id);
CREATE INDEX idx_loan_status ON fact_loan_performance(loan_status);
