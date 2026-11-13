-- ============================================================================
-- 05_financial_reports.sql
-- Financial Analytics and Risk Reporting System
-- P&L Aggregations, Month-over-Month (MoM), and Year-over-Year (YoY) Reports
-- ============================================================================

-- 1. Monthly Executive Profit & Loss Summary
WITH monthly_agg AS (
    SELECT 
        strftime('%Y-%m', date) AS report_month,
        SUM(revenue) AS total_revenue,
        SUM(cogs) AS total_cogs,
        SUM(revenue - cogs) AS gross_profit,
        SUM(total_opex) AS total_opex,
        SUM(ebitda) AS total_ebitda,
        SUM(ebit) AS total_ebit,
        SUM(interest_expense) AS total_interest,
        SUM(tax) AS total_tax,
        SUM(net_profit) AS total_net_profit
    FROM fact_general_ledger
    GROUP BY strftime('%Y-%m', date)
)
SELECT 
    report_month,
    total_revenue,
    total_cogs,
    gross_profit,
    ROUND((gross_profit * 1.0 / NULLIF(total_revenue, 0)) * 100, 2) AS gross_margin_pct,
    total_opex,
    total_ebitda,
    total_ebit,
    total_interest,
    total_tax,
    total_net_profit,
    ROUND((total_net_profit * 1.0 / NULLIF(total_revenue, 0)) * 100, 2) AS net_margin_pct
FROM monthly_agg
ORDER BY report_month ASC;

-- 2. Year-over-Year (YoY) Revenue and Net Profit Growth Analysis
WITH monthly_pnl AS (
    SELECT 
        strftime('%Y-%m', date) AS report_month,
        strftime('%Y', date) AS cal_year,
        strftime('%m', date) AS cal_month,
        SUM(revenue) AS monthly_revenue,
        SUM(net_profit) AS monthly_net_profit
    FROM fact_general_ledger
    GROUP BY strftime('%Y-%m', date), strftime('%Y', date), strftime('%m', date)
)
SELECT 
    curr.report_month,
    curr.monthly_revenue AS current_rev,
    prior.monthly_revenue AS prior_year_rev,
    ROUND(((curr.monthly_revenue - prior.monthly_revenue) * 1.0 / NULLIF(prior.monthly_revenue, 0)) * 100, 2) AS yoy_rev_growth_pct,
    curr.monthly_net_profit AS current_np,
    prior.monthly_net_profit AS prior_year_np,
    ROUND(((curr.monthly_net_profit - prior.monthly_net_profit) * 1.0 / NULLIF(prior.monthly_net_profit, 0)) * 100, 2) AS yoy_np_growth_pct
FROM monthly_pnl curr
LEFT JOIN monthly_pnl prior 
    ON CAST(curr.cal_year AS INT) = CAST(prior.cal_year AS INT) + 1 
    AND curr.cal_month = prior.cal_month
ORDER BY curr.report_month ASC;

-- 3. Rolling 3-Month Trailing Average Revenue and EBITDA
WITH monthly_series AS (
    SELECT 
        strftime('%Y-%m', date) AS report_month,
        SUM(revenue) AS rev,
        SUM(ebitda) AS ebitda
    FROM fact_general_ledger
    GROUP BY strftime('%Y-%m', date)
)
SELECT 
    report_month,
    rev AS monthly_revenue,
    ROUND(AVG(rev) OVER (ORDER BY report_month ROWS BETWEEN 2 PRECEDING AND CURRENT ROW), 2) AS rolling_3m_avg_revenue,
    ebitda AS monthly_ebitda,
    ROUND(AVG(ebitda) OVER (ORDER BY report_month ROWS BETWEEN 2 PRECEDING AND CURRENT ROW), 2) AS rolling_3m_avg_ebitda
FROM monthly_series
ORDER BY report_month ASC;

-- 4. Profitability by Region and Product Line
SELECT 
    region,
    product,
    SUM(revenue) AS total_revenue,
    SUM(gross_profit) AS total_gross_profit,
    ROUND((SUM(gross_profit) * 1.0 / NULLIF(SUM(revenue), 0)) * 100, 2) AS gross_margin_pct,
    SUM(net_profit) AS total_net_profit,
    ROUND((SUM(net_profit) * 1.0 / NULLIF(SUM(revenue), 0)) * 100, 2) AS net_margin_pct
FROM fact_general_ledger
GROUP BY region, product
ORDER BY total_revenue DESC;
