# Individual Project Reflection Template
**Financial Analytics and Risk Reporting System**
*14-Day Data Analytics & Risk Engineering Specialization Deliverable*

---

## 1. Contributor Identification
- **Team Member Name:** __________________________________
- **Primary Specialization Role:** (e.g., Financial Modeling Lead / Credit Risk Engineer / BI Dashboard Architect / Automation & Pipeline Engineer)
- **Period of Performance:** 20 October 2026 – 20 November 2026
- **Self-Assessment Rating (1 to 5):** _____ / 5

---

## 2. Workstream Deliverables Owned & Codebase Evidence

| Workstream Component | Specific Files & Artifacts Owned | Git Commit / PR Reference |
|---|---|---|
| **Data Ingestion & Staging** | `src/data_ingestion.py`, `src/data_cleaning.py`, `data/raw/`, `data/staging/` | `feat: build automated data ingestion and staging pipeline` |
| **Feature Engineering & Scorecard** | `src/feature_engineering.py`, `src/credit_scorecard.py`, `notebooks/04_credit_scorecard.ipynb` | `feat: develop WOE binned logistic credit scorecard` |
| **Financial Calculations & P&L** | `src/financial_calculations.py`, `sql/05_financial_reports.sql`, `excel/financial_model.xlsx` | `feat: implement P&L bridge, balance sheet, and budget variance` |
| **Interactive Dashboards** | `qlik/qlik_dashboard_documentation.md`, `excel/powerpivot_model_documentation.md` | `feat: build Qlik Sense semantic star schema and DAX measures` |
| **Automation & Reporting** | `src/automation.py`, `power_automate/board_pack_flow_documentation.md`, `reports/` | `feat: orchestrate monthly board pack PDF and flow` |
| **Testing & Quality Assurance** | `tests/test_*.py`, `sql/03_data_quality_checks.sql`, `docs/test_results.md` | `test: implement 33 unit tests and SQL data quality audit` |

---

## 3. Technical Skills Acquired & Deepened

1. **Weight of Evidence (WOE) & Information Value (IV) Analysis:**
   - Deepened understanding of continuous variable binning techniques (quantile and decision-tree binning) to capture non-linear default patterns without violating model interpretability.
   - Implemented strict Fair Lending governance rules to exclude protected attributes from model training data.
2. **Scorecard Point Scaling:**
   - Formulated logarithmic scaling transformations: $Score = Offset + Factor \times \ln(odds)$ with calibrated Points to Double the Odds (PDO = 30) and baseline odds (2:1).
3. **Double-Entry Financial Modeling & Analytical Star Schema:**
   - Engineered dimensional models matching operational General Ledger architectures, validating that balance sheets maintain $Assets = Liabilities + Equity$ at every month-end.
4. **End-to-End Test Automation with Pytest & SQL:**
   - Developed automated testing pipelines achieving 100% test pass rate across 33 unit tests and 6 database constraint audits.

---

## 4. Key Engineering Challenges & Solutions

### Challenge 1: Log-Odds Scaling & Risk Band Calibration
- **Context:** Initial baseline odds calibration ($50:1$) resulted in scores compressing into a narrow band because the empirical loan portfolio default rate was 36.5% rather than prime bank 2%.
- **Solution:** Re-calibrated the baseline odds parameter to match the portfolio average ($2:1$ good:bad odds at Base Score = 600) and established four distinct, defensible score cutoffs (Low: $\ge 630$, Medium: $600-629$, High: $560-599$, Very High: $< 560$).
- **Impact:** Achieved balanced risk distribution across all four underwriting tiers with clear expected loss pricing differentiation.

### Challenge 2: Multi-Layer Financial Reconciliation
- **Context:** Manual reporting historically resulted in discrepancies between General Ledger totals, departmental cost center allocations, and executive board presentations.
- **Solution:** Enforced strict programmatic reconciliation checks in `src/validation.py` and `sql/03_data_quality_checks.sql` that halt pipeline execution if arithmetic variance exceeds \$0.01.

---

## 5. Strategic Business Acumen Learned

- **Bridging the Finance-Risk Divide:** Financial executives focus on GAAP P&L margins and budget variances, while credit risk managers focus on vintage loss curves and concentration risks. This project demonstrated how integrating Expected Loss ($PD \times LGD \times EAD$) directly into budget variance reporting creates a unified operational picture.
- **Rule-Based Executive Commentary:** Moving beyond raw variance percentages to automated, driver-based commentary (volume vs price/mix vs credit migration) dramatically reduces executive review friction.

---

## 6. What Would Be Improved With Additional Time

1. **Macroeconomic Stress Testing:** Incorporate CECL/IFRS 9 forward-looking macroeconomic scenarios (baseline, adverse, severe adverse GDP and unemployment shocks).
2. **Dynamic Workout LGD Modeling:** Replace the static 45.0% LGD assumption with a machine-learning recovery model predicting workout recovery cash flows.
3. **Direct Qlik Cloud Webhook Integration:** Connect the Power Automate flow directly to Qlik Cloud APIs to trigger reload tasks without intermediate file writes.
