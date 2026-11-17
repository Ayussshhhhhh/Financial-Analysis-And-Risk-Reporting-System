# Semantic model design

## Grain and relationships

| Table | Grain | Relationship |
|---|---|---|
| DimDate | One row per calendar date | 1:* to sales order date and inventory snapshot date; mark as date table |
| DimProduct | One row per product | 1:* to sales and inventory |
| DimRegion | One row per source sales territory, with its sales-territory group | 1:* to sales; filter using `GroupName` (North America/Europe/Pacific) for regional security |
| FactSalesInternet | One order line | Many-to-one to Date, Product, Region; CustomerKey retained for approved drill-through |
| FactInventorySnapshot | One product per snapshot date | Many-to-one to Date and Product |
| FactHRMonthly | One month, region, department | Future approved aggregate source only |

Use single-direction dimension-to-fact filters. Do not join fact tables directly. CurrencyKey is retained: report source currency separately unless a valid rate table and conversion date are supplied. Sales amount is not silently summed across currencies. The base AW DW sample generally uses a consistent reporting currency in its internet sales fact, but confirm source currency keys before combining channels.

## Extensions

Add reseller sales as a second fact at order-line grain with shared Date/Product/Region dimensions. Add Customer/Reseller/Currency/Promotion dimensions from the source when needed. Finance, budget, and HR require separate validated source facts; do not treat sales cost as operating expense or gross profit as net income.

## Refresh

Full reload is the safe baseline for sample data. Date-key watermark or SQL Server Change Tracking can replace it once source change behavior and late-arriving records are validated. Preserve dimensions before inserting facts and run reconciliation after each refresh.
