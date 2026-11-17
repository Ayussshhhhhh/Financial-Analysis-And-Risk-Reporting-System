# File-Based Data Interface & Architecture Documentation
**Financial Analytics and Risk Reporting System**

---

## 1. Overview
The platform operates on a robust, auditable multi-tier file and database architecture. Each layer enforces strict schemas, data contracts, and validation rules to ensure data integrity across the reporting lifecycle.

```
+-------------------------------------------------------------------------------+
| 1. RAW LAYER (data/raw/)                                                      |
|    - loans_raw.csv (Lending Club loan origination data, 10,000 records)       |
|    - ledger_raw.csv (Monthly general ledger records, 4,200 records)           |
+-------------------------------------------------------------------------------+
                                        |
                                        v (src/data_cleaning.py)
+-------------------------------------------------------------------------------+
| 2. STAGING LAYER (data/staging/)                                              |
|    - stg_loans.csv (Standardized schema, imputed nulls, parsed datetimes)     |
|    - stg_ledger.csv (Standardized accounts, balanced journal entries)         |
+-------------------------------------------------------------------------------+
                                        |
                                        v (src/feature_engineering.py & SQL)
+-------------------------------------------------------------------------------+
| 3. CURATED LAYER (data/curated/financial_analytics.db)                       |
|    - fact_loan_performance (10,000 rows with PD, score points, EL, risk bands)|
|    - fact_general_ledger (4,200 rows with P&L line items)                     |
|    - fact_balance_sheet (4,200 rows with asset & liability reconciliations)   |
|    - fact_budget_actual (4,200 rows with variance drivers & commentary)       |
|    - dim_risk_band, dim_date, dim_region, dim_product                         |
+-------------------------------------------------------------------------------+
                                        |
                                        v (src/reporting.py & Qlik Sense)
+-------------------------------------------------------------------------------+
| 4. PRESENTATION & REPORTING LAYER (reports/ & excel/)                         |
|    - monthly_board_pack.pdf / .html (Executive C-Suite board pack)            |
|    - financial_report.xlsx (Dynamic formatted Excel P&L)                      |
|    - financial_model.xlsx (Complete financial model with working formulas)    |
|    - credit_risk_report.pdf / summary.xlsx                                    |
+-------------------------------------------------------------------------------+
```

---

## 2. Data Contracts & Schema Specifications

### `loans_raw.csv` / `stg_loans.csv`
- `loan_id` (String, Primary Key): Unique alphanumeric loan identifier.
- `loan_amnt` (Float, Numeric): Principal origination amount ($1,000 – $40,000). Must be positive.
- `term` (Integer): Term in months (36 or 60).
- `int_rate` (Float): Annualized interest rate (e.g. 11.50). Must be positive.
- `installment` (Float): Monthly payment obligation.
- `grade` (Categorical: A, B, C, D, E, F, G): Subprime to super-prime grade assigned at origination.
- `annual_inc` (Float): Self-reported borrower gross annual income.
- `dti` (Float): Debt-to-Income ratio percentage (0.00 – 60.00%).
- `default_flag` (Binary Float): Target variable. 1 = Default / Charged Off; 0 = Fully Paid; NaN = In-Progress (excluded from scorecard training).

### `ledger_raw.csv` / `stg_ledger.csv`
- `date` (Date, YYYY-MM-DD): Reporting month closing date.
- `region` (Categorical): North, South, East, West, Central.
- `product` (Categorical): Personal Loans, Auto Loans, Mortgages, Credit Cards, Business Loans.
- `department` (Categorical): Sales, Risk, Tech, Finance, Marketing, Ops, HR.
- `revenue`, `cogs`, `gross_profit`: Operational trading metrics.
- `total_assets`, `total_liabilities_equity`: Balance sheet position metrics. Must satisfy $|A - (L+E)| < 1.00$.

---

## 3. Data Refresh Process & Boundary Validation Rules

1. **Ingestion Boundary Check:** Ensures zero duplicate primary keys and valid date formats.
2. **Fair Lending Boundary Check:** Guarantees that protected demographic attributes (gender, race, ethnicity, religion) are excluded prior to feature engineering.
3. **Accounting Boundary Check:** Validates that $Revenue - COGS = Gross Profit$ and $Assets = Liabilities + Equity$ before database commit.
4. **Model Boundary Check:** Validates that scorecard discrimination meets minimum thresholds ($AUC \ge 0.65$, $KS \ge 0.25$) before risk-band assignment.
