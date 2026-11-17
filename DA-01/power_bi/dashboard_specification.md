# Dashboard page specification

Build a 16:9 report with a restrained navy/teal palette, consistent currency and percent formatting, explicit date range in titles, accessible contrast, and a persistent page navigation bar. All measures come from the semantic model.

| Page | Visuals | Interactions |
|---|---|---|
| Executive overview | Revenue, gross profit, gross margin, YoY cards; monthly trend; regional bar; category contribution; top products/customers; risk callouts; freshness | Date and region slicers; click region to drill-through |
| Sales performance | Monthly trend, channel comparison when reseller fact is added, category/subcategory bars, customer segment, top/bottom product table, order-line detail | Date/category/region slicers; detail page drill-through by region/product/order |
| Finance performance | Revenue, product cost, gross profit and margin trend; margin bridge only when validated finance expense data exists | Region/product/date filters |
| HR analytics | Headcount trend, hires/exits, attrition, tenure by department and region | Aggregate-only; restricted HR role |
| Supply chain | Inventory quantity/value (only with validated cost), low-stock table, days of supply, turnover trend | Product/region/date filters |
| Regional manager | Assigned-region KPIs, product/customer performance, targets when loaded, inventory risk where region attribution exists | RLS-scoped drill-through |
| Sales detail | Order number/line, date, product, quantity, amount, cost, gross profit | Drill-through; export governed by workspace policy |

A visual requiring unavailable target, HR, operating-profit, or inventory valuation inputs should be visibly labeled “source not connected” during a demo and omitted from the KPI totals. This is a source limitation, not a zero value. Do not include maps unless geographic attributes are reviewed and the regional mapping is correct.
