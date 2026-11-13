-- ============================================================================
-- 07_credit_risk.sql
-- Financial Analytics and Risk Reporting System
-- Credit Risk Scorecard Analytics, Expected Loss (EL), and Vintage Analysis
-- ============================================================================

-- 1. Credit Portfolio Breakdown by Risk Band
SELECT 
    risk_band,
    COUNT(*) AS total_loans,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM fact_loan_performance), 2) AS portfolio_share_pct,
    ROUND(AVG(scorecard_points), 1) AS avg_scorecard_points,
    ROUND(AVG(pd_estimate) * 100, 2) AS avg_pd_pct,
    ROUND(SUM(loan_amnt), 2) AS total_exposure_ead,
    ROUND(SUM(expected_loss), 2) AS total_expected_loss,
    ROUND((SUM(expected_loss) * 1.0 / NULLIF(SUM(loan_amnt), 0)) * 100, 2) AS expected_loss_rate_pct
FROM fact_loan_performance
GROUP BY risk_band
ORDER BY avg_scorecard_points DESC;

-- 2. Default Rate Analysis by Loan Grade
SELECT 
    grade,
    COUNT(*) AS loan_count,
    ROUND(AVG(int_rate), 2) AS avg_interest_rate,
    ROUND(AVG(loan_amnt), 2) AS avg_loan_amount,
    SUM(CASE WHEN default_flag = 1 THEN 1 ELSE 0 END) AS defaults_count,
    ROUND(AVG(CASE WHEN default_flag IS NOT NULL THEN default_flag END) * 100, 2) AS observed_default_rate_pct,
    ROUND(AVG(pd_estimate) * 100, 2) AS model_predicted_pd_pct
FROM fact_loan_performance
GROUP BY grade
ORDER BY grade ASC;

-- 3. Default Rate by Debt-to-Income (DTI) Bucket
SELECT 
    dti_bucket,
    COUNT(*) AS loan_count,
    ROUND(AVG(dti), 2) AS avg_dti,
    ROUND(AVG(CASE WHEN default_flag IS NOT NULL THEN default_flag END) * 100, 2) AS observed_default_rate_pct,
    ROUND(AVG(scorecard_points), 1) AS avg_scorecard_points
FROM fact_loan_performance
GROUP BY dti_bucket
ORDER BY avg_dti ASC;

-- 4. Default Rate by Income Bucket
SELECT 
    income_bucket,
    COUNT(*) AS loan_count,
    ROUND(AVG(annual_inc), 2) AS avg_annual_income,
    ROUND(AVG(CASE WHEN default_flag IS NOT NULL THEN default_flag END) * 100, 2) AS observed_default_rate_pct,
    ROUND(AVG(scorecard_points), 1) AS avg_scorecard_points
FROM fact_loan_performance
GROUP BY income_bucket
ORDER BY avg_annual_income ASC;

-- 5. Expected Loss (EL = PD x LGD x EAD) Summary by Grade and Term
SELECT 
    grade,
    term,
    COUNT(*) AS loan_count,
    ROUND(SUM(loan_amnt), 2) AS total_ead,
    ROUND(AVG(pd_estimate), 4) AS avg_pd,
    0.4500 AS assumed_lgd,
    ROUND(SUM(expected_loss), 2) AS portfolio_expected_loss,
    ROUND((SUM(expected_loss) / NULLIF(SUM(loan_amnt), 0)) * 100, 2) AS el_to_exposure_pct
FROM fact_loan_performance
GROUP BY grade, term
ORDER BY grade ASC, term ASC;

-- 6. Concentration Risk: Top 5 Segments by Total Exposure
SELECT 
    purpose,
    grade,
    COUNT(*) AS loan_count,
    ROUND(SUM(loan_amnt), 2) AS total_exposure,
    ROUND((SUM(loan_amnt) * 100.0 / (SELECT SUM(loan_amnt) FROM fact_loan_performance)), 2) AS portfolio_concentration_pct,
    ROUND(SUM(expected_loss), 2) AS segment_expected_loss
FROM fact_loan_performance
GROUP BY purpose, grade
ORDER BY total_exposure DESC
LIMIT 5;

-- 7. Vintage Analysis: Default Trajectory by Issue Quarter
SELECT 
    strftime('%Y-Q', issue_d) || ((CAST(strftime('%m', issue_d) AS INT) - 1) / 3 + 1) AS issue_vintage_quarter,
    COUNT(*) AS origination_count,
    ROUND(SUM(loan_amnt), 2) AS vintage_origination_volume,
    SUM(CASE WHEN default_flag = 1 THEN 1 ELSE 0 END) AS charged_off_count,
    ROUND(AVG(CASE WHEN default_flag IS NOT NULL THEN default_flag END) * 100, 2) AS cumulative_default_rate_pct,
    ROUND(AVG(scorecard_points), 1) AS vintage_avg_score
FROM fact_loan_performance
GROUP BY strftime('%Y-Q', issue_d) || ((CAST(strftime('%m', issue_d) AS INT) - 1) / 3 + 1)
ORDER BY issue_vintage_quarter ASC;
