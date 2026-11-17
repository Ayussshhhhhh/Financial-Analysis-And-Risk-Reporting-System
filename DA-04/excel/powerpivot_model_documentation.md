# Power Pivot Model Documentation
## Financial Analysis and Risk Reporting System

**Last Updated:** November 2026  
**Author:** Financial Systems Team  
**Version:** 2.1  
**Workbook:** `FinancialAnalysis_RiskReporting.xlsx`

---

## Table of Contents

1. [Data Model Overview](#1-data-model-overview)
2. [Table Relationships](#2-table-relationships)
3. [DAX Measures](#3-dax-measures)
4. [Power Query Transformation Steps](#4-power-query-transformation-steps)
5. [Pivot Table Configurations](#5-pivot-table-configurations)
6. [Refresh Instructions](#6-refresh-instructions)

---

## 1. Data Model Overview

### Star Schema Architecture

The Power Pivot data model is designed as a **star schema** comprising one or more central fact tables surrounded by descriptive dimension tables. This architecture optimises query performance, simplifies DAX authoring, and ensures referential integrity across all analytical views.

```
                        ┌─────────────────────┐
                        │     dim_date        │
                        │  (Date Dimension)   │
                        └──────────┬──────────┘
                                   │
                     ┌─────────────┼─────────────┐
                     │             │             │
          ┌──────────▼──────┐  ┌───▼──────────┐  │
          │ fact_general_   │  │ fact_budget_  │  │
          │    ledger       │  │   actual      │  │
          └──────────┬──────┘  └───┬──────────┘  │
                     │             │             │
         ┌───────────┼─────────────┘             │
         │           │                           │
┌────────▼──────┐  ┌─▼──────────────┐  ┌────────▼────────┐
│ dim_account   │  │  dim_cost_      │  │  fact_loan_     │
│  (COA)        │  │   center        │  │  performance    │
└───────────────┘  └────────────────┘  └────────┬────────┘
                                                  │
                                         ┌────────▼────────┐
                                         │  dim_borrower   │
                                         └─────────────────┘
```

### Fact Tables

| Table Name | Description | Rows (Approx.) | Grain |
|---|---|---|---|
| `fact_general_ledger` | Journal entries from ERP; actual financial amounts by account, cost center, and date | ~500,000 | One row per journal line |
| `fact_budget_actual` | Budgeted vs. actual amounts by account and period | ~120,000 | One row per account per month |
| `fact_loan_performance` | Lending Club loan-level data including PD, LGD, EAD, and performance flags | ~115,000 | One row per loan |

### Dimension Tables

| Table Name | Description | Primary Key | Rows (Approx.) |
|---|---|---|---|
| `dim_date` | Calendar dimension with fiscal attributes, week numbers, quarter labels | `date_key` (INT YYYYMMDD) | 3,653 (10 years) |
| `dim_account` | Chart of Accounts with account hierarchy, type classification, and reporting category | `account_code` | ~800 |
| `dim_cost_center` | Organisational hierarchy: Group → Division → Department → Cost Centre | `cost_center_id` | ~150 |
| `dim_borrower` | Borrower demographics: employment, home ownership, state, credit grade | `borrower_id` | ~115,000 |
| `dim_product` | Product/segment taxonomy for revenue analysis | `product_id` | ~50 |

### Model Storage Mode

All tables are loaded in **Import Mode** (VertiPaq in-memory columnar store). No DirectQuery tables are used. The model is compressed to approximately **180–240 MB** in-memory depending on data volume.

---

## 2. Table Relationships

All relationships are defined as single-directional (from dimension to fact) unless otherwise noted. Cross-filter direction is set to **Single** to prevent ambiguous filter propagation. Bidirectional cross-filtering is applied only where explicitly noted.

| # | From Table | From Column | To Table | To Column | Cardinality | Active | Cross-filter |
|---|---|---|---|---|---|---|---|
| 1 | `dim_date` | `date_key` | `fact_general_ledger` | `date_key` | One-to-Many | ✅ Yes | Single |
| 2 | `dim_date` | `date_key` | `fact_budget_actual` | `date_key` | One-to-Many | ✅ Yes | Single |
| 3 | `dim_date` | `date_key` | `fact_loan_performance` | `issue_date_key` | One-to-Many | ✅ Yes | Single |
| 4 | `dim_account` | `account_code` | `fact_general_ledger` | `account_code` | One-to-Many | ✅ Yes | Single |
| 5 | `dim_account` | `account_code` | `fact_budget_actual` | `account_code` | One-to-Many | ✅ Yes | Single |
| 6 | `dim_cost_center` | `cost_center_id` | `fact_general_ledger` | `cost_center_id` | One-to-Many | ✅ Yes | Single |
| 7 | `dim_cost_center` | `cost_center_id` | `fact_budget_actual` | `cost_center_id` | One-to-Many | ✅ Yes | Single |
| 8 | `dim_borrower` | `borrower_id` | `fact_loan_performance` | `borrower_id` | One-to-Many | ✅ Yes | Single |
| 9 | `dim_product` | `product_id` | `fact_general_ledger` | `product_id` | One-to-Many | ✅ Yes | Single |
| 10 | `dim_product` | `product_id` | `fact_budget_actual` | `product_id` | One-to-Many | ✅ Yes | Single |

### Relationship Notes

- **Relationship 3** uses `issue_date_key` as the loan origination date. A separate inactive relationship on `maturity_date_key` exists and is activated via `USERELATIONSHIP()` in maturity-based measures.
- **Relationship 1 and 2** both point to `dim_date`, enabling time-intelligence measures to work correctly across both fact tables.
- **Role-playing date dimension**: Two additional inactive relationships connect `dim_date.date_key` → `fact_loan_performance.close_date_key` for closed-loan analysis.

---

## 3. DAX Measures

All measures are stored in a dedicated hidden table called `_Measures` to keep the model clean. Formatting standards: Currency measures use `$#,##0.00`; percentage measures use `0.00%`; count measures use `#,##0`.

---

### Financial KPIs

#### Total Revenue
```dax
Total Revenue :=
CALCULATE(
    SUM(fact_general_ledger[actual_amount]),
    fact_general_ledger[account_type] = "Revenue"
)
```
**Description:** Sums all journal entries classified as Revenue account type. Respects all active slicers (date, cost center, product).  
**Format:** `$#,##0`  
**Display Folder:** `Financial KPIs`

---

#### Total COGS
```dax
Total COGS :=
CALCULATE(
    SUM(fact_general_ledger[actual_amount]),
    fact_general_ledger[account_type] = "COGS"
)
```
**Description:** Aggregates Cost of Goods Sold entries from the general ledger.  
**Format:** `$#,##0`  
**Display Folder:** `Financial KPIs`

---

#### Gross Profit
```dax
Gross Profit := [Total Revenue] - [Total COGS]
```
**Description:** Calculated as the difference between Total Revenue and Total COGS.  
**Format:** `$#,##0`  
**Display Folder:** `Financial KPIs`

---

#### Gross Margin %
```dax
Gross Margin % := DIVIDE([Gross Profit], [Total Revenue], 0)
```
**Description:** Gross Profit as a percentage of Total Revenue. Returns 0 if revenue is zero (safe division).  
**Format:** `0.00%`  
**Display Folder:** `Financial KPIs`

---

#### Total OpEx
```dax
Total OpEx :=
CALCULATE(
    SUM(fact_general_ledger[actual_amount]),
    fact_general_ledger[account_type] = "Operating Expense"
)
```
**Description:** Total Operating Expenses from the ledger. Excludes COGS, Interest, and Tax entries.  
**Format:** `$#,##0`  
**Display Folder:** `Financial KPIs`

---

#### Depreciation & Amortization
```dax
Depreciation & Amortization :=
CALCULATE(
    SUM(fact_general_ledger[actual_amount]),
    fact_general_ledger[account_name] IN {"Depreciation", "Amortization"}
)
```
**Description:** Filters the ledger for specific non-cash expense accounts named "Depreciation" and "Amortization". Used in EBITDA and EBIT calculations.  
**Format:** `$#,##0`  
**Display Folder:** `Financial KPIs`

---

#### EBITDA
```dax
EBITDA := [Gross Profit] - [Total OpEx] + [Depreciation & Amortization]
```
**Description:** Earnings Before Interest, Taxes, Depreciation, and Amortization. D&A is added back because it is already included within OpEx in the ledger.  
**Format:** `$#,##0`  
**Display Folder:** `Financial KPIs`

---

#### EBIT
```dax
EBIT := [EBITDA] - [Depreciation & Amortization]
```
**Description:** Earnings Before Interest and Taxes. Deducts D&A from EBITDA to arrive at operating income.  
**Format:** `$#,##0`  
**Display Folder:** `Financial KPIs`

---

#### Interest Expense
```dax
Interest Expense :=
CALCULATE(
    SUM(fact_general_ledger[actual_amount]),
    fact_general_ledger[account_type] = "Interest Expense"
)
```
**Description:** Total interest charges on debt obligations recorded in the general ledger.  
**Format:** `$#,##0`  
**Display Folder:** `Financial KPIs`

---

#### Tax Expense
```dax
Tax Expense :=
CALCULATE(
    SUM(fact_general_ledger[actual_amount]),
    fact_general_ledger[account_type] = "Tax"
)
```
**Description:** Total income tax expense as recorded in the ledger.  
**Format:** `$#,##0`  
**Display Folder:** `Financial KPIs`

---

#### Net Profit
```dax
Net Profit := [EBIT] - [Interest Expense] - [Tax Expense]
```
**Description:** Bottom-line profitability after all operating, interest, and tax charges.  
**Format:** `$#,##0`  
**Display Folder:** `Financial KPIs`

---

#### Net Margin %
```dax
Net Margin % := DIVIDE([Net Profit], [Total Revenue], 0)
```
**Description:** Net Profit as a percentage of Total Revenue. Key profitability ratio for executive reporting.  
**Format:** `0.00%`  
**Display Folder:** `Financial KPIs`

---

### Budget Variance Measures

#### Total Budget Revenue
```dax
Total Budget Revenue :=
CALCULATE(
    SUM(fact_budget_actual[budget_amount]),
    fact_budget_actual[account_type] = "Revenue"
)
```
**Description:** Budgeted revenue target from the budget planning file, filtered to Revenue account type.  
**Format:** `$#,##0`  
**Display Folder:** `Budget Variance`

---

#### Budget Variance
```dax
Budget Variance := [Total Revenue] - [Total Budget Revenue]
```
**Description:** Absolute variance between actual and budgeted revenue. Positive = Favorable, Negative = Unfavorable.  
**Format:** `$#,##0`  
**Display Folder:** `Budget Variance`

---

#### Budget Variance %
```dax
Budget Variance % := DIVIDE([Budget Variance], [Total Budget Revenue], 0)
```
**Description:** Variance expressed as a percentage of the budget. Used for threshold-based conditional formatting.  
**Format:** `0.00%`  
**Display Folder:** `Budget Variance`

---

#### Favorable Variance Flag
```dax
Favorable Variance Flag := IF([Budget Variance] > 0, "Favorable", "Unfavorable")
```
**Description:** Text label classifying the direction of budget variance. Used in slicers, conditional formatting rules, and narrative text boxes.  
**Format:** Text  
**Display Folder:** `Budget Variance`

---

### Time Intelligence Measures

> **Important:** All time intelligence measures require a continuous, uninterrupted date table (`dim_date`) marked as a **Date Table** in the Power Pivot model. The `full_date` column must be set as the date column.

#### Prior Month Revenue
```dax
Prior Month Revenue :=
CALCULATE(
    [Total Revenue],
    DATEADD(dim_date[full_date], -1, MONTH)
)
```
**Description:** Total Revenue for the calendar month immediately prior to the current filter context.  
**Format:** `$#,##0`  
**Display Folder:** `Time Intelligence`

---

#### MoM Revenue Growth
```dax
MoM Revenue Growth :=
DIVIDE(
    [Total Revenue] - [Prior Month Revenue],
    [Prior Month Revenue],
    0
)
```
**Description:** Month-over-Month growth rate of revenue. Returns 0 when prior month is blank (e.g., first period in dataset).  
**Format:** `0.00%`  
**Display Folder:** `Time Intelligence`

---

#### Prior Year Revenue
```dax
Prior Year Revenue :=
CALCULATE(
    [Total Revenue],
    DATEADD(dim_date[full_date], -1, YEAR)
)
```
**Description:** Total Revenue for the same period in the prior fiscal/calendar year.  
**Format:** `$#,##0`  
**Display Folder:** `Time Intelligence`

---

#### YoY Revenue Growth
```dax
YoY Revenue Growth :=
DIVIDE(
    [Total Revenue] - [Prior Year Revenue],
    [Prior Year Revenue],
    0
)
```
**Description:** Year-over-Year revenue growth rate. Essential for trend analysis and executive reporting.  
**Format:** `0.00%`  
**Display Folder:** `Time Intelligence`

---

#### YTD Revenue
```dax
YTD Revenue :=
CALCULATE(
    [Total Revenue],
    DATESYTD(dim_date[full_date])
)
```
**Description:** Cumulative revenue from January 1st of the current year through the last date in context. For fiscal year YTD, replace with `DATESYTD(dim_date[full_date], "03/31")` or the appropriate fiscal year-end date.  
**Format:** `$#,##0`  
**Display Folder:** `Time Intelligence`

---

#### Prior YTD Revenue
```dax
Prior YTD Revenue :=
CALCULATE(
    [Total Revenue],
    DATESYTD(DATEADD(dim_date[full_date], -1, YEAR))
)
```
**Description:** Cumulative revenue for the same year-to-date period in the prior year. Used for YTD vs. prior YTD comparison charts.  
**Format:** `$#,##0`  
**Display Folder:** `Time Intelligence`

---

### Credit Risk Measures

#### Total Loan Portfolio
```dax
Total Loan Portfolio := SUM(fact_loan_performance[ead])
```
**Description:** Total Exposure at Default (EAD) across all loans in the portfolio. Represents the total credit exposure.  
**Format:** `$#,##0`  
**Display Folder:** `Credit Risk`

---

#### Default Rate
```dax
Default Rate :=
DIVIDE(
    COUNTROWS(FILTER(fact_loan_performance, fact_loan_performance[default_flag] = 1)),
    COUNTROWS(fact_loan_performance),
    0
)
```
**Description:** Proportion of loans that have defaulted. `default_flag = 1` indicates confirmed default status. Respects all active dimension filters.  
**Format:** `0.00%`  
**Display Folder:** `Credit Risk`

---

#### Expected Loss Total
```dax
Expected Loss Total :=
SUMX(
    fact_loan_performance,
    fact_loan_performance[pd_estimate]
        * fact_loan_performance[lgd_assumption]
        * fact_loan_performance[ead]
)
```
**Description:** Row-by-row calculation of Expected Loss using the Basel formula: `EL = PD × LGD × EAD`. Aggregated across all loans in the current filter context.  
**Format:** `$#,##0`  
**Display Folder:** `Credit Risk`

---

#### Expected Loss % of Portfolio
```dax
Expected Loss % of Portfolio :=
DIVIDE(
    [Expected Loss Total],
    [Total Loan Portfolio],
    0
)
```
**Description:** Expected Loss as a percentage of total portfolio EAD. Key metric for ICAAP and risk appetite reporting.  
**Format:** `0.00%`  
**Display Folder:** `Credit Risk`

---

#### Average PD
```dax
Average PD :=
AVERAGEX(
    fact_loan_performance,
    fact_loan_performance[pd_estimate]
)
```
**Description:** Exposure-weighted average Probability of Default. Note: `AVERAGEX` computes a simple row average. For exposure-weighted average, replace numerator with `SUMX(fact_loan_performance, fact_loan_performance[pd_estimate] * fact_loan_performance[ead])` divided by `[Total Loan Portfolio]`.  
**Format:** `0.00%`  
**Display Folder:** `Credit Risk`

---

#### Delinquency Rate
```dax
Delinquency Rate :=
DIVIDE(
    COUNTROWS(FILTER(fact_loan_performance, fact_loan_performance[delinq_2yrs] > 0)),
    COUNTROWS(fact_loan_performance),
    0
)
```
**Description:** Fraction of loans that have had at least one delinquency event in the past 2 years (`delinq_2yrs > 0`). Used as an early-warning indicator.  
**Format:** `0.00%`  
**Display Folder:** `Credit Risk`

---

#### Average DTI
```dax
Average DTI := AVERAGE(fact_loan_performance[dti])
```
**Description:** Simple average Debt-to-Income ratio across all loans in context. Filtered views (e.g., by grade or state) automatically reflect the filtered population.  
**Format:** `0.00%`  
**Display Folder:** `Credit Risk`

---

## 4. Power Query Transformation Steps

Power Query (M language) transformations are defined in the **Queries & Connections** pane. Each query is set to **Load to Data Model** only (not to worksheet) to minimise file size.

---

### Query 1: LendingClub_Loans (CSV Ingestion)

**Source File:** `data/raw/lending_club_loans.csv`  
**Destination Table:** `fact_loan_performance`

```m
let
    // Step 1: Load source CSV file
    Source = Csv.Document(
        File.Contents("C:\FinancialReports\data\raw\lending_club_loans.csv"),
        [
            Delimiter       = ",",
            Columns         = 24,
            Encoding        = 65001,   // UTF-8
            QuoteStyle      = QuoteStyle.Csv
        ]
    ),

    // Step 2: Promote first row as column headers
    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),

    // Step 3: Select only required columns
    SelectedColumns = Table.SelectColumns(
        PromotedHeaders,
        {
            "id", "member_id", "loan_amnt", "funded_amnt", "term",
            "int_rate", "installment", "grade", "sub_grade",
            "emp_length", "home_ownership", "annual_inc", "loan_status",
            "dti", "delinq_2yrs", "open_acc", "pub_rec", "revol_bal",
            "revol_util", "total_acc", "addr_state", "issue_d",
            "purpose", "application_type"
        }
    ),

    // Step 4: Rename columns to snake_case standard names
    RenamedColumns = Table.RenameColumns(
        SelectedColumns,
        {
            {"id",           "loan_id"},
            {"member_id",    "borrower_id"},
            {"loan_amnt",    "loan_amount"},
            {"funded_amnt",  "funded_amount"},
            {"annual_inc",   "annual_income"},
            {"addr_state",   "state"},
            {"issue_d",      "issue_date"},
            {"loan_status",  "loan_status_raw"}
        }
    ),

    // Step 5: Set correct data types
    TypedColumns = Table.TransformColumnTypes(
        RenamedColumns,
        {
            {"loan_id",       type text},
            {"borrower_id",   type text},
            {"loan_amount",   type number},
            {"funded_amount", type number},
            {"term",          type text},
            {"int_rate",      type number},
            {"installment",   type number},
            {"grade",         type text},
            {"sub_grade",     type text},
            {"emp_length",    type text},
            {"home_ownership",type text},
            {"annual_income", type number},
            {"dti",           type number},
            {"delinq_2yrs",   Int64.Type},
            {"open_acc",      Int64.Type},
            {"pub_rec",       Int64.Type},
            {"revol_bal",     type number},
            {"revol_util",    type number},
            {"total_acc",     Int64.Type},
            {"state",         type text},
            {"issue_date",    type date},
            {"purpose",       type text},
            {"application_type", type text},
            {"loan_status_raw",  type text}
        }
    ),

    // Step 6: Clean int_rate — remove "%" if stored as text before cast
    CleanIntRate = Table.TransformColumns(
        TypedColumns,
        {
            {"int_rate", each if _ is text then Number.FromText(Text.Remove(_, {"%", " "})) else _}
        }
    ),

    // Step 7: Derive default_flag from loan status
    AddDefaultFlag = Table.AddColumn(
        CleanIntRate,
        "default_flag",
        each if List.Contains(
                {"Default", "Charged Off", "Does not meet the credit policy. Status:Charged Off"},
                [loan_status_raw]
             )
             then 1 else 0,
        Int64.Type
    ),

    // Step 8: Derive EAD (Exposure at Default) = funded_amount as a proxy
    AddEAD = Table.AddColumn(
        AddDefaultFlag,
        "ead",
        each [funded_amount],
        type number
    ),

    // Step 9: Add PD estimate — placeholder; real PD comes from Python model output
    // During initial load, set pd_estimate = 0; merge from model scores table later
    AddPD = Table.AddColumn(
        AddEAD,
        "pd_estimate",
        each 0.0,
        type number
    ),

    // Step 10: Add LGD assumption = 0.45 (industry standard for unsecured consumer loans)
    AddLGD = Table.AddColumn(
        AddPD,
        "lgd_assumption",
        each 0.45,
        type number
    ),

    // Step 11: Derive issue_date_key for relationship to dim_date
    AddDateKey = Table.AddColumn(
        AddLGD,
        "issue_date_key",
        each if [issue_date] = null then null
             else Date.Year([issue_date]) * 10000
                + Date.Month([issue_date]) * 100
                + Date.Day([issue_date]),
        Int64.Type
    ),

    // Step 12: Remove rows with null loan_id or loan_amount
    FilterNulls = Table.SelectRows(
        AddDateKey,
        each [loan_id] <> null and [loan_amount] <> null and [loan_amount] > 0
    ),

    // Step 13: Remove duplicate loan IDs (keep first occurrence)
    RemoveDuplicates = Table.Distinct(FilterNulls, {"loan_id"})

in
    RemoveDuplicates
```

---

### Query 2: SyntheticLedger (General Ledger CSV Ingestion)

**Source File:** `data/raw/synthetic_financial_data.csv`  
**Destination Table:** `fact_general_ledger`

```m
let
    // Step 1: Connect to synthetic ledger CSV
    Source = Csv.Document(
        File.Contents("C:\FinancialReports\data\raw\synthetic_financial_data.csv"),
        [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]
    ),

    // Step 2: Promote headers
    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),

    // Step 3: Select required columns
    SelectedColumns = Table.SelectColumns(
        PromotedHeaders,
        {
            "journal_id", "posting_date", "account_code", "account_name",
            "account_type", "cost_center_id", "product_id",
            "actual_amount", "currency", "description", "fiscal_year",
            "fiscal_period", "entity_id"
        }
    ),

    // Step 4: Apply data types
    TypedColumns = Table.TransformColumnTypes(
        SelectedColumns,
        {
            {"journal_id",    type text},
            {"posting_date",  type date},
            {"account_code",  type text},
            {"account_name",  type text},
            {"account_type",  type text},
            {"cost_center_id",type text},
            {"product_id",    type text},
            {"actual_amount", type number},
            {"currency",      type text},
            {"description",   type text},
            {"fiscal_year",   Int64.Type},
            {"fiscal_period", Int64.Type},
            {"entity_id",     type text}
        }
    ),

    // Step 5: Normalise account_type values to controlled vocabulary
    NormaliseAccountType = Table.TransformColumns(
        TypedColumns,
        {
            {
                "account_type",
                each let mapped = [
                        Revenue          = "Revenue",
                        Sales            = "Revenue",
                        COGS             = "COGS",
                        #"Cost of Sales" = "COGS",
                        #"Operating Expense" = "Operating Expense",
                        OpEx             = "Operating Expense",
                        #"Interest Expense"  = "Interest Expense",
                        Tax              = "Tax",
                        Depreciation     = "Operating Expense",
                        Amortization     = "Operating Expense"
                    ]
                in if Record.HasFields(mapped, _) then Record.Field(mapped, _) else _,
                type text
            }
        }
    ),

    // Step 6: Add date_key for relationship to dim_date
    AddDateKey = Table.AddColumn(
        NormaliseAccountType,
        "date_key",
        each Date.Year([posting_date]) * 10000
           + Date.Month([posting_date]) * 100
           + Date.Day([posting_date]),
        Int64.Type
    ),

    // Step 7: Remove journal entries with zero amounts (saves model size)
    FilterZero = Table.SelectRows(
        AddDateKey,
        each [actual_amount] <> 0 and [actual_amount] <> null
    ),

    // Step 8: Convert non-USD amounts using static FX rate table
    // (Assumes USD base; extend with dynamic FX table if multi-currency)
    AddUSDAmount = Table.AddColumn(
        FilterZero,
        "actual_amount_usd",
        each if [currency] = "USD" then [actual_amount]
             else if [currency] = "GBP" then [actual_amount] * 1.27
             else if [currency] = "EUR" then [actual_amount] * 1.09
             else [actual_amount],   // default: no conversion
        type number
    ),

    // Step 9: Sort by posting_date ascending
    SortedRows = Table.Sort(AddUSDAmount, {{"posting_date", Order.Ascending}})

in
    SortedRows
```

---

### Query 3: BudgetData (Excel Budget File Ingestion)

**Source File:** `data/raw/budget_2024.xlsx`  
**Destination Table:** `fact_budget_actual`

```m
let
    // Step 1: Connect to Excel workbook
    Source = Excel.Workbook(
        File.Contents("C:\FinancialReports\data\raw\budget_2024.xlsx"),
        null,
        true
    ),

    // Step 2: Navigate to the "Budget_Detail" named sheet/table
    BudgetSheet = Source{[Item = "Budget_Detail", Kind = "Sheet"]}[Data],

    // Step 3: Promote first row as headers
    PromotedHeaders = Table.PromoteHeaders(BudgetSheet, [PromoteAllScalars = true]),

    // Step 4: Remove empty rows introduced by Excel formatting
    RemovedBlanks = Table.SelectRows(
        PromotedHeaders,
        each not List.IsEmpty(List.RemoveMatchingItems(Record.FieldValues(_), {"", null}))
    ),

    // Step 5: Select and rename required columns
    SelectedColumns = Table.SelectColumns(
        RemovedBlanks,
        {
            "Account Code", "Account Name", "Account Type", "Cost Center",
            "Product", "Budget Period", "Budget Amount", "Entity"
        }
    ),

    RenamedColumns = Table.RenameColumns(
        SelectedColumns,
        {
            {"Account Code",   "account_code"},
            {"Account Name",   "account_name"},
            {"Account Type",   "account_type"},
            {"Cost Center",    "cost_center_id"},
            {"Product",        "product_id"},
            {"Budget Period",  "budget_period"},
            {"Budget Amount",  "budget_amount"},
            {"Entity",         "entity_id"}
        }
    ),

    // Step 6: Parse budget_period from "YYYY-MM" text format to date
    AddBudgetDate = Table.AddColumn(
        RenamedColumns,
        "budget_date",
        each let
            parts = Text.Split([budget_period], "-"),
            yr    = Number.FromText(parts{0}),
            mo    = Number.FromText(parts{1})
        in #date(yr, mo, 1),
        type date
    ),

    // Step 7: Add date_key
    AddDateKey = Table.AddColumn(
        AddBudgetDate,
        "date_key",
        each Date.Year([budget_date]) * 10000
           + Date.Month([budget_date]) * 100
           + Date.Day([budget_date]),
        Int64.Type
    ),

    // Step 8: Apply data types
    TypedColumns = Table.TransformColumnTypes(
        AddDateKey,
        {
            {"account_code",  type text},
            {"account_name",  type text},
            {"account_type",  type text},
            {"cost_center_id",type text},
            {"product_id",    type text},
            {"budget_period", type text},
            {"budget_amount", type number},
            {"entity_id",     type text},
            {"budget_date",   type date},
            {"date_key",      Int64.Type}
        }
    ),

    // Step 9: Filter out rows where budget_amount is null or zero
    FilterNulls = Table.SelectRows(
        TypedColumns,
        each [budget_amount] <> null and [budget_amount] <> 0
    )

in
    FilterNulls
```

---

## 5. Pivot Table Configurations

### PivotTable 1: Monthly P&L Summary

**Sheet:** `P&L Dashboard`  
**Purpose:** Management P&L view by month with YoY comparison.

| Configuration Item | Setting |
|---|---|
| Data Source | Power Pivot Data Model |
| Report Filter | `dim_date[fiscal_year]`, `dim_cost_center[division]` |
| Column Labels | `dim_date[month_year_label]` (e.g., "Jan-24") |
| Row Labels | `dim_account[account_type]`, `dim_account[account_name]` |
| Values (1) | `[Total Revenue]` — Format: `$#,##0` |
| Values (2) | `[Gross Profit]` — Format: `$#,##0` |
| Values (3) | `[Net Profit]` — Format: `$#,##0` |
| Values (4) | `[Net Margin %]` — Format: `0.00%` |
| Values (5) | `[YoY Revenue Growth]` — Format: `0.00%` |
| Subtotals | Show for Account Type rows only |
| Grand Totals | Show for Columns (yearly total) |
| Conditional Formatting | Data bar on `[Net Profit]`; Red/Green icon set on `[Net Margin %]` (threshold: < 5% = Red, 5–15% = Yellow, > 15% = Green) |

---

### PivotTable 2: Budget vs. Actual Variance Report

**Sheet:** `Budget Variance`  
**Purpose:** Monthly budget tracking for Finance Controller review.

| Configuration Item | Setting |
|---|---|
| Data Source | Power Pivot Data Model |
| Report Filter | `dim_date[fiscal_year]`, `dim_product[product_name]` |
| Column Labels | `dim_date[month_year_label]` |
| Row Labels | `dim_account[account_type]`, `dim_cost_center[department_name]` |
| Values (1) | `[Total Budget Revenue]` — Format: `$#,##0` |
| Values (2) | `[Total Revenue]` — Format: `$#,##0` |
| Values (3) | `[Budget Variance]` — Format: `$#,##0` |
| Values (4) | `[Budget Variance %]` — Format: `0.00%` |
| Values (5) | `[Favorable Variance Flag]` — Format: Text |
| Conditional Formatting | `[Budget Variance]`: Green fill for positive, Red fill for negative values using "Format only cells that contain" rule |
| Sort | Sorted by `[Budget Variance]` ascending (worst variances at top) |

---

### PivotTable 3: Credit Risk Portfolio Summary

**Sheet:** `Credit Risk`  
**Purpose:** Loan portfolio risk metrics for Risk Officer review.

| Configuration Item | Setting |
|---|---|
| Data Source | Power Pivot Data Model |
| Report Filter | `dim_borrower[state]`, `dim_date[fiscal_year]` |
| Column Labels | `dim_borrower[grade]` (A, B, C, D, E, F, G) |
| Row Labels | `dim_borrower[home_ownership]`, `dim_borrower[emp_length]` |
| Values (1) | `[Total Loan Portfolio]` — Format: `$#,##0` |
| Values (2) | `[Default Rate]` — Format: `0.00%` |
| Values (3) | `[Expected Loss Total]` — Format: `$#,##0` |
| Values (4) | `[Average PD]` — Format: `0.00%` |
| Values (5) | `[Delinquency Rate]` — Format: `0.00%` |
| Values (6) | `[Average DTI]` — Format: `0.00%` |
| Conditional Formatting | Heat map colour scale on `[Default Rate]`: White → Yellow → Red |
| Sort | Columns sorted by `[Default Rate]` descending |

---

### PivotTable 4: Time Intelligence Revenue Trend

**Sheet:** `Revenue Trend`  
**Purpose:** Trend analysis with MoM and YoY growth for business review meetings.

| Configuration Item | Setting |
|---|---|
| Data Source | Power Pivot Data Model |
| Report Filter | `dim_product[product_name]`, `dim_cost_center[region]` |
| Column Labels | None (single column per measure) |
| Row Labels | `dim_date[fiscal_year]`, `dim_date[month_name]` |
| Values (1) | `[Total Revenue]` — Format: `$#,##0` |
| Values (2) | `[Prior Month Revenue]` — Format: `$#,##0` |
| Values (3) | `[MoM Revenue Growth]` — Format: `0.00%` |
| Values (4) | `[YTD Revenue]` — Format: `$#,##0` |
| Values (5) | `[YoY Revenue Growth]` — Format: `0.00%` |
| Conditional Formatting | Up/Down arrow icon sets on `[MoM Revenue Growth]` and `[YoY Revenue Growth]` |
| Sparklines | Column sparklines on `[Total Revenue]` for the most recent 12 months |

---

### PivotTable 5: Department Profitability Matrix

**Sheet:** `Department P&L`  
**Purpose:** Cross-tab of P&L metrics by department and product for operational reviews.

| Configuration Item | Setting |
|---|---|
| Data Source | Power Pivot Data Model |
| Report Filter | `dim_date[fiscal_year]`, `dim_date[fiscal_period]` |
| Column Labels | `dim_product[product_category]` |
| Row Labels | `dim_cost_center[division]`, `dim_cost_center[department_name]` |
| Values (1) | `[Total Revenue]` — Format: `$#,##0` |
| Values (2) | `[Total OpEx]` — Format: `$#,##0` |
| Values (3) | `[EBITDA]` — Format: `$#,##0` |
| Values (4) | `[Gross Margin %]` — Format: `0.00%` |
| Subtotals | Show for Division level |
| Grand Totals | On for both rows and columns |
| Conditional Formatting | 3-colour scale on `[EBITDA]` by column; threshold-based formatting on `[Gross Margin %]` (< 20% = Red, 20–40% = Yellow, > 40% = Green) |
| Layout | Outline form with repeated item labels for readability |

---

## 6. Refresh Instructions

### Pre-Refresh Checklist

Before initiating a data refresh, verify the following:

1. ✅ All source CSV/Excel files are in their expected paths (see Query configurations above).
2. ✅ The `lending_club_loans.csv` file has been updated with the latest monthly extract from the data warehouse.
3. ✅ The `synthetic_financial_data.csv` has been exported from the ERP system for the reporting period.
4. ✅ The `budget_2024.xlsx` file has been signed off by the Finance Controller.
5. ✅ No other users have the Excel workbook open (shared network drive conflict risk).
6. ✅ Available RAM ≥ 4 GB (Power Pivot loads full dataset into memory).

---

### Manual Refresh Steps

**Step 1: Open the Workbook**
- Navigate to `C:\FinancialReports\FinancialAnalysis_RiskReporting.xlsx`
- Open in Microsoft Excel (desktop — not Excel Online, which does not support Power Pivot refresh)

**Step 2: Navigate to Power Pivot**
- Click the **Power Pivot** tab in the Excel ribbon
- Click **Manage** to open the Power Pivot window

**Step 3: Refresh All Queries**
- In the Power Pivot window, click **Home** → **Refresh** → **Refresh All**
- Alternatively, return to Excel and use **Data** tab → **Refresh All** (Ctrl + Alt + F5)

**Step 4: Monitor Refresh Progress**
- A progress dialog will appear showing each table being refreshed
- Typical refresh times: `LendingClub_Loans` ~45–90 seconds; `SyntheticLedger` ~20–40 seconds; `BudgetData` ~5–10 seconds

**Step 5: Review Refresh Errors**
- If any table fails, the dialog will show an error message with the table name
- Common errors:
  - `File not found` → Verify source file path in Power Query Editor
  - `Type conversion error` → Check source data for unexpected values in typed columns
  - `Memory error` → Close other applications and retry

**Step 6: Verify Row Counts**
- In the Power Pivot window, check the row count at the bottom of each table view:
  - `fact_general_ledger`: Expected ≥ 400,000 rows
  - `fact_loan_performance`: Expected ≥ 100,000 rows
  - `fact_budget_actual`: Expected ≥ 100,000 rows

**Step 7: Verify Pivot Table Output**
- Return to the `P&L Dashboard` sheet
- Confirm `[Total Revenue]` for the current month matches the ERP control total
- Confirm `[Default Rate]` is within expected bounds (typically 5–20% depending on portfolio grade)

**Step 8: Save the Workbook**
- Use **File → Save** (not Save As) to preserve connections
- File size after refresh: typically 180–280 MB

---

### Scheduled Automated Refresh (via Power Automate)

For automated monthly refresh without manual intervention, the Power Automate board pack flow (see `power_automate/board_pack_flow_documentation.md`) triggers a Windows Desktop Flow that:

1. Opens the Excel workbook on a Windows Server VM
2. Executes the `RefreshAllConnections()` VBA macro
3. Saves and closes the workbook
4. Uploads the refreshed file to SharePoint

**VBA Macro for Automated Refresh:**

```vba
Sub RefreshAllConnections()
    Dim conn As WorkbookConnection
    Application.ScreenUpdating = False
    Application.Calculation = xlCalculationManual

    ' Refresh all Power Query connections
    For Each conn In ThisWorkbook.Connections
        conn.Refresh
    Next conn

    ' Force recalculation of all pivot tables
    Dim pt As PivotTable
    Dim ws As Worksheet
    For Each ws In ThisWorkbook.Worksheets
        For Each pt In ws.PivotTables
            pt.RefreshTable
        Next pt
    Next ws

    Application.Calculation = xlCalculationAutomatic
    Application.ScreenUpdating = True
    ThisWorkbook.Save
    MsgBox "Refresh complete. All tables and pivots updated.", vbInformation
End Sub
```

---

*End of Power Pivot Model Documentation — v2.1*
