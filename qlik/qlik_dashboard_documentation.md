# Qlik Sense Dashboard Architecture & Implementation Specification
**Financial Analytics and Risk Reporting System**
*Interactive Business Intelligence & Decision Support Suite*

---

## 1. Overview & Semantic Model Architecture

The Qlik Sense analytical application connects directly to the Curated SQLite data layer (`data/curated/financial_analytics.db`) and curated dimensional tables.

```
                              +-----------------------+
                              |      dim_date         |
                              +-----------------------+
                                          |
        +---------------------------------+---------------------------------+
        |                                 |                                 |
        v                                 v                                 v
+-----------------------+     +-----------------------+     +-----------------------+
|  fact_general_ledger  |     |  fact_budget_actual   |     | fact_loan_performance |
+-----------------------+     +-----------------------+     +-----------------------+
        |                                 |                                 |
        +---------------------------------+---------------------------------+
                                          |
               +--------------------------+--------------------------+
               |                          |                          |
               v                          v                          v
     +-------------------+      +-------------------+      +-------------------+
     |    dim_region     |      |    dim_product    |      |   dim_risk_band   |
     +-------------------+      +-------------------+      +-------------------+
```

---

## 2. Global Filter Panel & Color Semantics

### Global Filter Bar (Present on all 4 sheets)
- **Time Selection:** `Year`, `Quarter`, `Month` (Derived from `dim_date`)
- **Organizational Hierarchy:** `Region`, `Department`
- **Product Hierarchy:** `Product Name`, `Product Category`
- **Risk Segmentation:** `Risk Band`, `Credit Grade`

### Corporate Color Palette Standard
- 🟢 **Favorable Variance / Low Risk:** `#27AE60` (Green)
- 🟡 **Warning / Moderate Variance / Medium Risk:** `#F39C12` (Amber)
- 🔴 **Unfavorable Variance / High Risk:** `#E74C3C` (Red)
- 🔵 **Primary Brand / Baseline:** `#1F497D` (Navy Blue)

---

## 3. Detailed Dashboard Sheet Specifications

### Sheet 1: Executive Summary
Designed for the **CFO, CRO, and Board of Directors** to assess enterprise health at a glance.

#### Key Visualizations
1. **Top KPI Row Cards:**
   - **Total Operating Revenue:**
     ```qlik
     Num(Sum({<account_type={'Revenue'}>} actual_amount), '$#,##0')
     ```
   - **Net Profit Margin %:**
     ```qlik
     Num(Sum({<account_type={'Net Profit'}>} actual_amount) / Sum({<account_type={'Revenue'}>} actual_amount), '0.0%')
     ```
   - **Budget Revenue Variance:**
     ```qlik
     Num(Sum({<metric_name={'Revenue'}>} variance), '$#,##0')
     ```
   - **Portfolio Expected Loss (EL):**
     ```qlik
     Num(Sum(expected_loss), '$#,##0')
     ```
2. **Monthly Revenue & Net Profit Trend (Combo Chart):**
   - *Dimension:* `MonthYear`
   - *Bar Measure:* `Total Revenue`
   - *Line Measure:* `Net Profit`
3. **Budget Variance Gauge:**
   - Needle indicating current YTD variance against budget thresholds.
4. **Credit Risk Exposure by Band (Donut Chart):**
   - *Dimension:* `risk_band`
   - *Measure:* `Sum(loan_amnt)`

---

### Sheet 2: Profitability & P&L Analysis
Designed for **Finance Analysts and FP&A Directors** for financial drill-downs.

#### Key Visualizations
1. **P&L Financial Waterfall Bridge:**
   - Visualizes steps from `Gross Revenue` $\to$ `- COGS` $\to$ `= Gross Profit` $\to$ `- OpEx` $\to$ `= EBITDA` $\to$ `- D&A` $\to$ `= EBIT` $\to$ `- Interest & Tax` $\to$ `= Net Profit`.
2. **Gross Margin & Net Margin by Product Line (Horizontal Stacked Bar):**
   - *Dimension:* `product`
   - *Measures:* `Gross Margin %`, `Net Margin %`
3. **OpEx Breakdown by Cost Center (Treemap):**
   - *Dimensions:* `department`, `account_name`
   - *Measure:* `Sum(actual_amount)`
4. **Detailed General Ledger Drill-Down Table:**
   - Full transactional exploration with multi-level dimension expand/collapse.

---

### Sheet 3: Credit Risk & Scorecard Analytics
Designed for the **Head of Credit Underwriting & Risk Management**.

#### Key Visualizations
1. **Risk Scorecard Points Distribution (Histogram):**
   - *Dimension:* Score buckets (30-point intervals: `500-530`, `530-560`, etc.)
   - *Measure:* Loan count split by Good vs Charged-Off borrowers.
2. **Risk Band Concentration & Migration Matrix:**
   - Table showing `Loan Count`, `Exposure at Default (EAD)`, `Average PD %`, `Expected Loss ($)`, and `Expected Loss Rate %`.
3. **Default Rate by DTI & Income Matrix (Heatmap):**
   - *X-Axis:* `dti_bucket` (`0-15`, `15-25`, `25-35`, `35+`)
   - *Y-Axis:* `income_bucket` (`Q1`, `Q2`, `Q3`, `Q4`)
   - *Cell Color:* Default rate gradient from green to dark red.
4. **Vintage Curve Cohort Analysis (Line Chart):**
   - *Dimension:* Months on books (`MOB`)
   - *Lines:* Origination Quarter cohorts (`2024-Q1`, `2024-Q2`, etc.)
   - *Measure:* Cumulative Charge-Off %

---

### Sheet 4: Budget vs. Actual Variance & Driver Explorer
Designed for **Operational Department Heads and Business Unit Leaders**.

#### Key Visualizations
1. **Budget vs. Actual Variance Waterfall:**
   - Shows total company plan variance decomposed by Department.
2. **Pareto Chart of Top 10 Unfavorable Variances:**
   - *Dimension:* `Department / Account`
   - *Bar:* Absolute Variance ($)
   - *Line:* Cumulative % of Total Negative Variance.
3. **Dynamic Rule-Based Variance Driver Commentary Table:**
   - Features automated natural language commentary generated from Python variance engine:
     ```qlik
     If(variance < 0, 
        'Unfavorable variance of ' & Num(Abs(variance), '$#,##0') & ' driven by ' & commentary,
        'Favorable variance of ' & Num(variance, '$#,##0') & ' outperforming budget.')
     ```

---

## 4. Qlik Sense Data Load Script (QVS Snippet)

```qlik
// ============================================================================
// Main Load Script: Connect via ODBC/SQLite
// ============================================================================
LIB CONNECT TO 'FinancialAnalytics_DB';

[fact_loan_performance]:
LOAD 
    loan_id,
    customer_id,
    product_id,
    risk_band,
    loan_status,
    default_flag,
    pd_estimate,
    scorecard_points,
    expected_loss,
    loan_amnt,
    issue_d,
    Date(issue_d, 'YYYY-MM') AS [IssueMonthYear]
FROM [fact_loan_performance];

[fact_general_ledger]:
LOAD 
    date,
    Date(date, 'YYYY-MM') AS [MonthYear],
    region,
    product,
    department,
    revenue,
    cogs,
    gross_profit,
    total_opex,
    ebitda,
    ebit,
    net_profit
FROM [fact_general_ledger];

[fact_budget_actual]:
LOAD 
    period,
    metric_name,
    actual,
    budget,
    variance,
    variance_pct,
    is_favorable,
    commentary
FROM [fact_budget_actual];
```

---

## 5. Automated PDF Export via Qlik NPrinting / Mail Service
- **Frequency:** 1st business day of each month at 07:00 AM UTC.
- **Output:** Formatted high-resolution PDF Board Pack.
- **Trigger:** Scheduled task or webhook invocation from Power Automate.
