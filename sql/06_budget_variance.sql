-- ============================================================================
-- 06_budget_variance.sql
-- Financial Analytics and Risk Reporting System
-- Budget vs. Actual Variance Reporting, Pareto Driver Ranking & Trend Analysis
-- ============================================================================

-- 1. Monthly Budget vs. Actual Performance Summary
SELECT 
    period,
    metric_name,
    SUM(budget) AS total_budget,
    SUM(actual) AS total_actual,
    SUM(variance) AS net_variance,
    ROUND((SUM(variance) * 1.0 / NULLIF(SUM(budget), 0)) * 100, 2) AS variance_pct,
    CASE WHEN SUM(variance) >= 0 THEN 'FAVORABLE' ELSE 'UNFAVORABLE' END AS overall_status
FROM fact_budget_actual
GROUP BY period, metric_name
ORDER BY period ASC;

-- 2. Top 10 Unfavorable Variances (Pareto Analysis)
SELECT 
    period,
    metric_name,
    budget,
    actual,
    variance,
    ROUND(variance_pct * 100, 2) AS variance_pct,
    commentary
FROM fact_budget_actual
WHERE is_favorable = 0
ORDER BY variance ASC
LIMIT 10;

-- 3. Top 10 Favorable Variances
SELECT 
    period,
    metric_name,
    budget,
    actual,
    variance,
    ROUND(variance_pct * 100, 2) AS variance_pct,
    commentary
FROM fact_budget_actual
WHERE is_favorable = 1
ORDER BY variance DESC
LIMIT 10;

-- 4. Cumulative Year-to-Date (YTD) Budget Variance Trajectory
WITH monthly_var AS (
    SELECT 
        period,
        SUM(actual) AS m_actual,
        SUM(budget) AS m_budget,
        SUM(variance) AS m_variance
    FROM fact_budget_actual
    GROUP BY period
)
SELECT 
    period,
    m_actual,
    m_budget,
    m_variance,
    SUM(m_actual) OVER (ORDER BY period ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS ytd_actual,
    SUM(m_budget) OVER (ORDER BY period ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS ytd_budget,
    SUM(m_variance) OVER (ORDER BY period ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS ytd_variance,
    ROUND((SUM(m_variance) OVER (ORDER BY period ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) * 1.0 /
          NULLIF(SUM(m_budget) OVER (ORDER BY period ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW), 0)) * 100, 2) AS ytd_variance_pct
FROM monthly_var
ORDER BY period ASC;
