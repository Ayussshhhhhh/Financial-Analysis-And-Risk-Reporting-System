-- ============================================================================
-- 03_data_quality_checks.sql
-- Financial Analytics and Risk Reporting System
-- Automated Data Quality Audit and Integrity Verification
-- ============================================================================

-- 1. Check for Nulls in Critical Loan Fields
SELECT 
    'fact_loan_performance Null Check' AS check_name,
    COUNT(*) AS total_records,
    SUM(CASE WHEN loan_id IS NULL THEN 1 ELSE 0 END) AS null_loan_id,
    SUM(CASE WHEN loan_amnt IS NULL OR loan_amnt <= 0 THEN 1 ELSE 0 END) AS invalid_loan_amnt,
    SUM(CASE WHEN pd_estimate IS NULL OR pd_estimate < 0 OR pd_estimate > 1 THEN 1 ELSE 0 END) AS invalid_pd,
    SUM(CASE WHEN scorecard_points IS NULL THEN 1 ELSE 0 END) AS null_scorecard_points,
    CASE 
        WHEN SUM(CASE WHEN loan_id IS NULL OR loan_amnt <= 0 OR pd_estimate < 0 OR pd_estimate > 1 THEN 1 ELSE 0 END) = 0 
        THEN 'PASSED' 
        ELSE 'FAILED' 
    END AS status
FROM fact_loan_performance;

-- 2. Check for Duplicate Loan IDs
SELECT 
    'Duplicate Loan ID Check' AS check_name,
    COUNT(loan_id) - COUNT(DISTINCT loan_id) AS duplicate_count,
    CASE WHEN COUNT(loan_id) = COUNT(DISTINCT loan_id) THEN 'PASSED' ELSE 'FAILED' END AS status
FROM fact_loan_performance;

-- 3. Balance Sheet Accounting Equation Validation (Total Assets = Liabilities + Equity)
SELECT 
    'Balance Sheet Accounting Equation (A = L + E)' AS check_name,
    COUNT(*) AS total_months_checked,
    ROUND(MAX(ABS(total_assets - (total_liabilities + equity))), 4) AS max_discrepancy,
    CASE 
        WHEN MAX(ABS(total_assets - (total_liabilities + equity))) < 1.00 THEN 'PASSED'
        ELSE 'FAILED'
    END AS status
FROM (
    SELECT 
        total_assets,
        (accounts_payable + short_term_debt + long_term_debt) AS total_liabilities,
        equity
    FROM fact_balance_sheet
);

-- 4. Budget Variance Arithmetic Integrity (Variance = Actual - Budget)
SELECT 
    'Budget Variance Calculation Audit' AS check_name,
    COUNT(*) AS total_records,
    ROUND(MAX(ABS(variance - (actual - budget))), 4) AS max_arithmetic_diff,
    CASE 
        WHEN MAX(ABS(variance - (actual - budget))) < 0.01 THEN 'PASSED'
        ELSE 'FAILED'
    END AS status
FROM fact_budget_actual;

-- 5. Scorecard Points and Risk Band Alignment Check
SELECT 
    'Scorecard Risk Band Cutoff Verification' AS check_name,
    risk_band,
    MIN(scorecard_points) AS min_points,
    MAX(scorecard_points) AS max_points,
    ROUND(AVG(pd_estimate) * 100, 2) AS avg_pd_pct,
    COUNT(*) AS loan_count,
    'PASSED' AS status
FROM fact_loan_performance
GROUP BY risk_band;

-- 6. Negative Value Sanity Check on Non-Negative Fields
SELECT 
    'Non-Negative Financials Check' AS check_name,
    SUM(CASE WHEN gl.revenue < 0 THEN 1 ELSE 0 END) AS negative_revenue_count,
    SUM(CASE WHEN gl.cogs < 0 THEN 1 ELSE 0 END) AS negative_cogs_count,
    SUM(CASE WHEN bs.total_assets < 0 THEN 1 ELSE 0 END) AS negative_assets_count,
    CASE 
        WHEN SUM(CASE WHEN gl.revenue < 0 OR gl.cogs < 0 OR bs.total_assets < 0 THEN 1 ELSE 0 END) = 0 
        THEN 'PASSED' 
        ELSE 'FAILED' 
    END AS status
FROM fact_general_ledger gl
JOIN fact_balance_sheet bs ON gl.date = bs.date;
