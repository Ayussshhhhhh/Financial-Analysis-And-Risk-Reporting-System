# Test Suite Execution & Quality Audit Results
**Financial Analytics and Risk Reporting System**
*Automated QA Verification Report*

---

## 1. Test Suite Summary

- **Framework:** `pytest 9.0.2` on `Python 3.11.9`
- **Total Tests Executed:** **33**
- **Passed:** **33 (100%)**
- **Failed:** **0**
- **Execution Time:** **0.09s**

```
============================= test session starts ==============================
platform darwin -- Python 3.11.9, pytest-9.0.2
collected 33 items

tests/test_data_quality.py::test_no_nulls_in_critical_loan_fields PASSED [  3%]
tests/test_data_quality.py::test_no_duplicate_loan_ids PASSED            [  6%]
tests/test_data_quality.py::test_issue_date_valid_range PASSED           [  9%]
tests/test_data_quality.py::test_loan_amnt_positive PASSED               [ 12%]
tests/test_data_quality.py::test_annual_inc_positive PASSED              [ 15%]
tests/test_data_quality.py::test_dti_in_valid_range PASSED               [ 18%]
tests/test_data_quality.py::test_default_flag_binary PASSED              [ 21%]
tests/test_data_quality.py::test_default_flag_no_ambiguous_status PASSED [ 24%]
tests/test_data_quality.py::test_assets_equal_liabilities_plus_equity PASSED [ 27%]
tests/test_data_quality.py::test_staging_files_exist PASSED              [ 30%]
tests/test_financial_calculations.py::test_gross_profit_equals_revenue_minus_cogs PASSED [ 33%]
tests/test_financial_calculations.py::test_net_profit_calculation PASSED [ 36%]
tests/test_financial_calculations.py::test_gross_margin_percentage PASSED [ 39%]
tests/test_financial_calculations.py::test_ebitda_calculation PASSED     [ 42%]
tests/test_financial_calculations.py::test_budget_variance_equals_actual_minus_budget PASSED [ 45%]
tests/test_financial_calculations.py::test_favorable_variance_flag PASSED [ 48%]
tests/test_financial_calculations.py::test_unfavorable_variance_flag PASSED [ 51%]
tests/test_financial_calculations.py::test_mom_change_calculation PASSED [ 54%]
tests/test_financial_calculations.py::test_yoy_change_calculation PASSED [ 57%]
tests/test_financial_calculations.py::test_variance_percentage_calculation PASSED [ 60%]
tests/test_financial_calculations.py::test_variance_percentage_zero_budget PASSED [ 63%]
tests/test_scorecard.py::test_woe_good_above_bad PASSED                  [ 66%]
tests/test_scorecard.py::test_woe_calculation_formula PASSED             [ 69%]
tests/test_scorecard.py::test_iv_always_positive PASSED                  [ 72%]
tests/test_scorecard.py::test_iv_range_interpretation PASSED             [ 75%]
tests/test_scorecard.py::test_model_predicts_valid_probabilities PASSED  [ 78%]
tests/test_scorecard.py::test_model_auc_above_chance PASSED              [ 81%]
tests/test_scorecard.py::test_scorecard_score_in_valid_range PASSED      [ 84%]
tests/test_scorecard.py::test_higher_pd_lower_score PASSED               [ 87%]
tests/test_scorecard.py::test_all_records_assigned_band PASSED           [ 90%]
tests/test_scorecard.py::test_risk_band_valid_values PASSED              [ 93%]
tests/test_scorecard.py::test_expected_loss_between_zero_and_ead PASSED  [ 96%]
tests/test_scorecard.py::test_expected_loss_formula PASSED               [100%]

============================== 33 passed in 0.09s ==============================
```

---

## 2. In-Pipeline Automated Data Quality & Audit Results (8 Checks)

| Check Description | Target Constraint | Measured Result | Audit Status |
|---|---|---|---|
| **P&L Gross Profit Identity** | $|GP - (Rev - COGS)| < 1.00$ | Max Diff: \$0.0100 | ✅ PASSED |
| **P&L Net Profit Identity** | $|NP - (EBIT - Int - Tax)| < 1.00$ | Max Diff: \$0.0000 | ✅ PASSED |
| **Balance Sheet Balance (A = L + E)** | $|Assets - (Liab + Equity)| < 1.00$ | Max Diff: \$0.0300 | ✅ PASSED |
| **Scorecard Discrimination (AUC)** | $AUC \ge 0.65$ | **0.6997** | ✅ PASSED |
| **Scorecard Gini Coefficient** | $Gini \ge 0.30$ | **0.3994** | ✅ PASSED |
| **Scorecard Separation (KS)** | $KS \ge 0.25$ | **0.3024** | ✅ PASSED |
| **Risk Band Complete Coverage** | Null count == 0; 4 valid bands | 0 nulls; 100% categorized | ✅ PASSED |
| **Expected Loss Bounds** | $0 \le EL \le EAD$ | 100% compliant | ✅ PASSED |

---

## 3. SQL Data Quality Checks (6 Checks Executed in Database)

| SQL Check Name | Tested Table | Findings | Status |
|---|---|---|---|
| **Loan Performance Nulls** | `fact_loan_performance` | 0 null IDs, 0 invalid EAD, 0 invalid PD | ✅ PASSED |
| **Duplicate Loan IDs** | `fact_loan_performance` | 0 duplicates across 10,000 records | ✅ PASSED |
| **Accounting Balance Check** | `fact_balance_sheet` | Max discrepancy \$0.03 across 4,200 rows | ✅ PASSED |
| **Budget Variance Math** | `fact_budget_actual` | Max difference \$0.00 across 4,200 rows | ✅ PASSED |
| **Scorecard Cutoff Integrity** | `fact_loan_performance` | Monotonic PD & points across all 4 bands | ✅ PASSED |
| **Non-Negative Values Check** | `fact_general_ledger` | 0 negative revenues, 0 negative assets | ✅ PASSED |

---

## 4. Known Limitations & Trade-Offs

1. **Synthetic Ledger Companion:** Because public lending datasets (e.g. Lending Club) do not bundle enterprise general ledgers, companion ledger records were synthesized using GAAP-compliant rules and seasonality.
2. **LGD Assumption:** Loss Given Default (LGD) is parameterized at a conservative 45.0% flat industry standard. In a full production bank environment, a dedicated two-stage Beta regression or Workout LGD model would be calibrated against post-default recovery cashflows.
