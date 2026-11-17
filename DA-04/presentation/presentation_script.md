# Presentation Script — Financial Analytics and Risk Reporting System
### 10-Minute Speaker Script with Timing Notes

> **Presenter Notes:** Read through this script at least twice before the session. Speak at a steady, conversational pace — aim for roughly 130 words per minute. Each section header includes a recommended time bracket. Use the `[PAUSE]` markers to let key points land, and use `[SLIDE X]` to advance the deck.

---

## [SLIDE 1] Title Slide

**[0:00–0:15]**

Good morning / Good afternoon, everyone. Thank you for joining us today.

My name is [Presenter Name], and on behalf of our team, I'd like to walk you through the **Financial Analytics and Risk Reporting System** — an end-to-end data pipeline we designed and built to automate profit-and-loss reporting, credit scoring, and board pack generation for a mid-sized financial institution.

Over the next ten minutes, we'll cover the business problem that motivated this project, the technical architecture, the key analytical outputs, and the measurable impact this system delivers.

Let's get started.

---

## [SLIDE 2] The Problem Statement

**[0:15–1:00]**

[SLIDE 2]

To understand why we built this system, we need to understand what it replaced.

[PAUSE]

The finance team was spending **three or more days every single month** manually pulling data from multiple source systems — the ERP, the loan management system, and several departmental spreadsheets — merging them in Excel, reconciling mismatches, and assembling a board pack that was out of date almost as soon as it was printed.

The consequences were significant. First, there was no **audit trail**. When a number changed between drafts, no one could explain why. Second, different teams were using **inconsistent KPI definitions** — EBITDA meant one thing to the finance team and something slightly different to the operations team. Third, manual processes introduced a **15% error rate** — small but serious in a regulated financial environment.

[PAUSE]

The question we asked ourselves was: *What if we could reduce that three-day reconciliation cycle to two hours, eliminate manual errors, and produce a consistent, auditable board pack automatically every month?*

That is exactly what this system does.

---

## [SLIDE 3] Architecture & Technology Stack

**[1:00–2:30]**

[SLIDE 3]

Let me walk you through how the system is designed at a high level.

[PAUSE]

Data flows in from two primary sources: a **synthetic loan portfolio** of 50,000 records representing the institution's credit book, and a **general ledger** containing 10,000 accounting transactions covering 24 months of history.

That raw data is ingested through a **Python-based ETL pipeline**. We use `pandas` for transformation and cleaning — handling missing values, standardising date formats, normalising currency fields, and deriving calculated columns. The cleaned data is loaded into a **SQLite database** structured as a star schema with 13 tables, including fact tables for loan events and ledger transactions, and dimension tables for accounts, customers, products, time, and risk bands.

[PAUSE]

On top of that database, we built two analytical layers. The first is a **financial reporting engine** that runs SQL queries to produce P&L statements, balance sheet snapshots, and budget variance analyses. The second is a **credit scorecard model** built in Python using `scikit-learn`, with Weight of Evidence variable selection and logistic regression.

The outputs are surfaced through **four Qlik Sense dashboards** for interactive exploration, and through a **Power Automate flow** that runs on the first business day of each month to generate a PDF board pack and email it to distribution lists.

[PAUSE]

The full stack is: **Python 3.10**, `pandas`, `scikit-learn`, `SQLite`, `Jupyter Notebooks` for development and documentation, **Qlik Sense** for dashboarding, and **Microsoft Power Automate** for orchestration.

Everything is version-controlled in Git, and 32 automated `pytest` tests guard against regressions.

---

## [SLIDE 4] Financial Reporting — P&L Results

**[2:30–4:30]**

[SLIDE 4]

Now let's look at the actual numbers. I want to emphasise that these figures come from our synthetic dataset — they are realistic but not derived from a live institution.

[PAUSE]

For **FY2024**, the system produced the following headline P&L:

- **Total Revenue: $12,423,890**
- **Cost of Goods Sold: $7,454,334**, leaving a **Gross Profit of $4,969,556** — a **Gross Margin of 40.0%**
- After operating expenses of $1,754,322, we arrive at an **EBITDA of $3,215,234**, which is **25.9% of revenue**
- After depreciation, interest, and a 23% tax provision, **Net Profit lands at $1,987,822** — a **Net Margin of 16.0%**

[PAUSE]

Crucially, the system automatically compares actuals to budget. Full-year revenue came in **$423,890 above budget** — a **4.5% favorable variance** — driven primarily by stronger-than-expected Q3 performance in the retail lending segment.

[SLIDE 5]

The Balance Sheet summary shows **Total Assets of $38.4 million**, funded by **$21.7 million in liabilities** and **$16.7 million in equity**, giving a **Debt-to-Equity ratio of 1.30** — within the institution's target range of 1.0 to 1.5.

[PAUSE]

What makes this powerful is not just the numbers themselves, but the speed and reliability with which they are produced. The system refreshes these reports in under **90 seconds** from trigger to output, with a complete audit log of every transformation applied to get from raw source data to final figure.

Previously, assembling even a draft P&L took a full day of analyst time. Now it is an automated morning task.

---

## [SLIDE 6] Credit Scorecard — Methodology

**[4:30–5:45]**

[SLIDE 6]

Moving to the credit risk side of the system. We built an application-stage credit scorecard — the kind of model that determines whether a loan applicant is approved and at what rate.

[PAUSE]

The methodology follows industry best practice in four stages:

**Stage one** is variable selection using **Weight of Evidence (WOE) and Information Value (IV)**. We evaluated 18 candidate variables from the loan application data. Variables with an IV below 0.02 were excluded as having negligible predictive power. The five highest-IV variables were: credit utilisation ratio (IV = 0.42), debt-to-income ratio (IV = 0.38), derogatory marks (IV = 0.31), loan purpose (IV = 0.24), and employment length (IV = 0.19).

[PAUSE]

**Stage two** is fitting a **logistic regression** model on WOE-transformed inputs. We used a 70/30 train-test split with stratified sampling to preserve the default rate in each partition.

**Stage three** is **score conversion** — mapping the log-odds output of the regression to an integer scorecard on a 300–850 scale, with 50-point odds doubling at a base score of 600.

**Stage four** is **risk band assignment**: scores 720 and above are Low Risk; 620–719 are Medium Risk; 500–619 are High Risk; and below 500 are Very High Risk.

---

## [SLIDE 7] Credit Scorecard — Model Performance

**[5:45–7:00]**

[SLIDE 7]

The model performs well by standard credit risk benchmarks.

[PAUSE]

The **Area Under the ROC Curve (AUC) is 0.812**. In plain language, this means that if you randomly select one defaulter and one non-defaulter from the portfolio, the model correctly ranks the defaulter as riskier 81.2% of the time. Industry guidance considers AUC above 0.75 to be a good model.

The **Gini coefficient is 0.624** — derived as `2 × AUC − 1`. This measures how much better the model discriminates compared to random chance.

The **Kolmogorov-Smirnov statistic is 0.483**, representing the maximum separation between the cumulative default and non-default distributions across all score thresholds. A KS above 0.40 is considered strong for a credit scorecard.

[PAUSE]

Translating these statistics to business impact: at the High Risk threshold, the model captures **74% of all future defaulters** in the top 30% of the risk distribution, meaning the institution can apply enhanced due diligence or reduce credit limits for a targeted segment rather than blanket restrictions.

[SLIDE 8]

For the full portfolio of **$45 million in Exposure at Default**, the model estimates a total **Expected Loss of $3.2 million — 7.1% of the portfolio**. That expected loss is allocated across risk bands:

- Low Risk: $0.4M (12% of EL, 48% of portfolio)
- Medium Risk: $1.1M (34% of EL, 33% of portfolio)
- High Risk: $1.3M (41% of EL, 15% of portfolio)
- Very High Risk: $0.4M (13% of EL, 4% of portfolio)

[PAUSE]

This concentration analysis tells management exactly where their risk capital is working hardest.

---

## [SLIDE 9] Dashboards & Automation

**[7:00–8:30]**

[SLIDE 9]

The analytical outputs are made available to business users through four **Qlik Sense dashboards**.

[PAUSE]

**Dashboard One: Executive KPI Overview.** A single-screen view of the top six financial and risk KPIs, with traffic-light status indicators and month-on-month trend sparklines. Designed for the CFO and CEO to consume in under two minutes.

**Dashboard Two: P&L and Budget Variance Drill-Down.** An interactive income statement where users can filter by time period, cost centre, or product line, and drill from summary level to individual transaction detail.

**Dashboard Three: Credit Portfolio Monitor.** A live view of the loan book by risk band, geography, product type, and vintage. Includes a delinquency heatmap and a 12-month expected loss trend.

**Dashboard Four: Scorecard Performance Tracker.** ROC curve, KS chart, score distribution histogram, and Population Stability Index (PSI) over time — the monitoring tools a risk analyst uses to validate that the model remains predictive as the portfolio evolves.

[SLIDE 10]

[PAUSE]

The **Power Automate orchestration flow** runs at 6 AM on the first business day of each month. It triggers a Python script on the report server, which queries the database and generates a formatted PDF board pack. If the script completes successfully, the PDF is emailed to the board distribution list with an executive summary in the email body. If the script fails, an alert is sent to the finance team inbox and the error is logged to an audit table in the database.

The entire flow — from trigger to delivered PDF — completes in under four minutes.

---

## [SLIDE 11] Testing & Validation

**[8:30–9:30]**

[SLIDE 11]

We're committed to production-grade code quality. The system has **32 automated `pytest` tests** organised across five test suites:

- **ETL Pipeline Tests (8 tests):** Schema validation, null handling, duplicate detection, type coercion
- **Financial Calculations Tests (10 tests):** P&L line-item accuracy, margin calculations, YTD accumulation
- **Credit Model Tests (6 tests):** WOE monotonicity, score range bounds, risk band boundary conditions
- **Automation Tests (5 tests):** Flow trigger, PDF generation, email dispatch simulation
- **Integration Tests (3 tests):** End-to-end pipeline from raw CSV to dashboard query result

All 32 tests pass. Code coverage is **85%**, measured with `pytest-cov`.

[PAUSE]

We want to be transparent about the system's current limitations. The data is **entirely synthetic** — generated using controlled random processes calibrated to realistic financial distributions. This means model performance metrics reflect the synthetic data-generating process, not real-world loan book behaviour. Additionally, the system operates in **batch mode** — there are no real-time data feeds, so the board pack reflects a point-in-time snapshot rather than an intraday view.

---

## [SLIDE 12] Business Impact & Next Steps

**[9:30–10:00]**

[SLIDE 12]

Let me close with what this system actually delivers.

[PAUSE]

The headline metric: **report generation time reduced from three days to two hours** — a **94% reduction** in analyst effort on the monthly close cycle. That is roughly **36 hours of analyst time saved per month**, or approximately **432 hours per year**.

Beyond time savings, the system delivers **auditability** — every figure in the board pack can be traced back to its source transaction. It delivers **consistency** — KPI definitions are encoded once in SQL and applied identically across every report. And it delivers **scalability** — adding a new data source or report section is a matter of adding a new module, not rebuilding a spreadsheet from scratch.

[PAUSE]

Looking ahead, the roadmap has three priorities. First, **connect to the real Lending Club API** to replace synthetic data with live loan performance observations. Second, **add an ML forecasting layer** using ARIMA or Prophet models for revenue and default rate projection. Third, **migrate the database to PostgreSQL and deploy on AWS RDS** so the system can serve multiple concurrent users and handle enterprise data volumes.

[PAUSE]

Thank you very much. We're happy to take questions, and we're particularly interested in your feedback on the credit risk methodology and the automation design.

---

*End of Script — Total Estimated Duration: 10:00*

> **Post-Presentation Notes:** Have the Qlik dashboards open in a browser tab and the Power Automate flow diagram ready for the Q&A section. If asked about scalability, reference the star schema design and the modularity of the ETL pipeline. If asked about data privacy, explain the synthetic data generation approach and reference the SKILL.md data governance section.
