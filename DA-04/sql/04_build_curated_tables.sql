-- ============================================================================
-- 04_build_curated_tables.sql
-- Financial Analytics and Risk Reporting System
-- Curated Analytical Star Schema Data Loading & Population Logic
-- ============================================================================

-- 1. Populate dim_date from date sequences
INSERT OR REPLACE INTO dim_date (
    date_key, full_date, year, quarter, month, month_name, week, day, is_weekend, is_month_end, fiscal_year, fiscal_quarter
)
SELECT 
    CAST(strftime('%Y%m%d', date) AS INT) AS date_key,
    date AS full_date,
    CAST(strftime('%Y', date) AS INT) AS year,
    ((CAST(strftime('%m', date) AS INT) - 1) / 3) + 1 AS quarter,
    CAST(strftime('%m', date) AS INT) AS month,
    CASE CAST(strftime('%m', date) AS INT)
        WHEN 1 THEN 'January' WHEN 2 THEN 'February' WHEN 3 THEN 'March'
        WHEN 4 THEN 'April' WHEN 5 THEN 'May' WHEN 6 THEN 'June'
        WHEN 7 THEN 'July' WHEN 8 THEN 'August' WHEN 9 THEN 'September'
        WHEN 10 THEN 'October' WHEN 11 THEN 'November' WHEN 12 THEN 'December'
    END AS month_name,
    CAST(strftime('%W', date) AS INT) AS week,
    CAST(strftime('%d', date) AS INT) AS day,
    CASE WHEN strftime('%w', date) IN ('0', '6') THEN 1 ELSE 0 END AS is_weekend,
    1 AS is_month_end,
    CAST(strftime('%Y', date) AS INT) AS fiscal_year,
    ((CAST(strftime('%m', date) AS INT) - 1) / 3) + 1 AS fiscal_quarter
FROM (
    SELECT DISTINCT date FROM fact_general_ledger
);

-- 2. Populate dim_region
INSERT OR REPLACE INTO dim_region (region_id, region_name, region_code, country)
VALUES 
    (1, 'North', 'NOR', 'United States'),
    (2, 'South', 'SOU', 'United States'),
    (3, 'East', 'EAS', 'United States'),
    (4, 'West', 'WES', 'United States'),
    (5, 'Central', 'CEN', 'United States');

-- 3. Populate dim_department
INSERT OR REPLACE INTO dim_department (dept_id, dept_name, dept_code, cost_center)
VALUES 
    (101, 'Sales & Origination', 'SALES', 'CC-101'),
    (102, 'Underwriting & Risk', 'RISK', 'CC-102'),
    (103, 'Technology & Data', 'TECH', 'CC-103'),
    (104, 'Finance & Accounting', 'FIN', 'CC-104'),
    (105, 'Marketing & Growth', 'MKT', 'CC-105'),
    (106, 'Operations & Servicing', 'OPS', 'CC-106'),
    (107, 'Human Resources', 'HR', 'CC-107');

-- 4. Populate dim_product
INSERT OR REPLACE INTO dim_product (product_id, product_name, product_category, interest_type, term_months)
VALUES 
    (1, 'Personal Loans', 'Unsecured Consumer', 'Fixed', 36),
    (2, 'Auto Loans', 'Secured Consumer', 'Fixed', 60),
    (3, 'Residential Mortgages', 'Real Estate', 'Fixed', 360),
    (4, 'Revolving Credit Cards', 'Unsecured Revolving', 'Variable', 12),
    (5, 'Small Business Loans', 'Commercial', 'Fixed', 48);

-- 5. Populate dim_risk_band
INSERT OR REPLACE INTO dim_risk_band (risk_band_id, risk_band_name, min_score, max_score, expected_pd_low, expected_pd_high, color_code)
VALUES 
    (1, 'Low Risk', 650.0, 850.0, 0.0000, 0.0500, '#5CB85C'),
    (2, 'Medium Risk', 600.0, 649.9, 0.0500, 0.1500, '#5BC0DE'),
    (3, 'High Risk', 550.0, 599.9, 0.1500, 0.3000, '#F0AD4E'),
    (4, 'Very High Risk', 300.0, 549.9, 0.3000, 1.0000, '#D9534F');
