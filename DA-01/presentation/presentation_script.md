# 10-minute final presentation script

## 0:00–1:00 — Business problem and objectives
Regional leaders need one trusted view of revenue, margin, workforce, and stock. Reporting fragmentation creates slow reconciliation and delays risk detection. This implementation demonstrates a governed multi-domain reporting foundation using AdventureWorksDW and explicitly separates available sample data from future source integrations.

## 1:00–2:30 — Architecture and pipeline
Show `docs/architecture.md`. The source is AdventureWorksDW; SQL stages selected facts, validates them, and builds curated dimensions/facts. SQL Agent is the runnable local schedule; the ADF design maps the same procedures into copy, quality, curated-load, audit, and alert steps. Power Query consumes curated tables and Power BI provides the semantic layer.

## 2:30–4:00 — Star schema and measures
Walk through `power_bi/semantic_model.md`: order-line sales grain, product/date/territory dimensions, snapshot grain for inventory, single-direction relationships. Demonstrate revenue, gross profit/margin, YTD, prior year, growth, and rolling average. Clarify that internet sales gross profit is not operating profit and no unverified target/HR values are fabricated.

## 4:00–6:00 — Dashboard walkthrough
Use the report built from `power_bi/dashboard_specification.md`: executive cards and trends, sales/category analysis, regional performance, product detail, and eligible drill-through. Explain slicer interactions and date context. Only show actual screenshots/report visuals captured from Power BI Desktop; this repository contains specifications, not fake screenshots.

## 6:00–7:30 — RLS demonstration
In Power BI Desktop choose View as and test North America, Europe, Pacific, and executive identities. Confirm region results and no rows for an unmapped identity. Show the separate workspace/model strategy that protects HR and finance from sales-detail access; RLS alone is not table security.

## 7:30–8:30 — Testing, refresh, governance
Show Python test run and SQL validation script. Explain SQL row/amount reconciliation, grain and foreign-key checks, audit status, failed-run alert branch, and explicit pending environment checks. Do not claim SQL Server or Service tests passed unless actually executed.

## 8:30–9:30 — Results and business impact
The result is a repeatable source package, governed sales model, secure regional access pattern, and deployment path. Quantified savings or business outcomes need a measured baseline and actual user adoption; this sample does not claim invented impact figures.

## 9:30–10:00 — Challenges, next steps, reflection
The sample's major limits are absent HR events, targets, operating expenses, and live tenant services. Next: connect approved sources, validate currency and regional attribution, publish to tenant, and capture real test evidence. Each contributor uses `individual_reflection.md` to document owned work and evidence.
