# DAX measure library

Assumptions: `DimDate[FullDate]` is marked as the date table and has a contiguous calendar; facts are related by date keys. Format currency with the model's reporting currency. Base sales is internet channel only. `DIVIDE` handles zero denominators; prior-period growth returns blank when no prior period exists.

```DAX
Total Sales = SUM(FactSalesInternet[SalesAmount])
Total Cost = SUM(FactSalesInternet[TotalProductCost])
Gross Profit = [Total Sales] - [Total Cost]
Gross Margin Percentage = DIVIDE([Gross Profit], [Total Sales])
Total Orders = DISTINCTCOUNT(FactSalesInternet[SalesOrderNumber])
Total Quantity Sold = SUM(FactSalesInternet[OrderQuantity])
Average Order Value = DIVIDE([Total Sales], [Total Orders])
Sales YTD = TOTALYTD([Total Sales], DimDate[FullDate])
Sales Prior Year = CALCULATE([Total Sales], SAMEPERIODLASTYEAR(DimDate[FullDate]))
Sales Year-over-Year Growth = [Total Sales] - [Sales Prior Year]
Sales Year-over-Year Growth Percentage = DIVIDE([Sales Year-over-Year Growth], [Sales Prior Year])
Sales Prior Month = CALCULATE([Total Sales], DATEADD(DimDate[FullDate], -1, MONTH))
Sales Month-over-Month Growth = DIVIDE([Total Sales]-[Sales Prior Month], [Sales Prior Month])
Rolling 3-Month Sales Average =
VAR EndDate = MAX(DimDate[FullDate])
VAR Period = DATESINPERIOD(DimDate[FullDate], EndDate, -3, MONTH)
RETURN DIVIDE(CALCULATE([Total Sales], Period), 3)
Rolling 12-Month Sales Average =
VAR EndDate = MAX(DimDate[FullDate])
VAR Period = DATESINPERIOD(DimDate[FullDate], EndDate, -12, MONTH)
RETURN DIVIDE(CALCULATE([Total Sales], Period), 12)
Inventory Quantity = SUM(FactInventorySnapshot[InventoryQuantity])
Inventory Turnover = DIVIDE([Total Cost], [Average Inventory Value])
Days of Supply = DIVIDE([Inventory Quantity], DIVIDE([Total Quantity Sold], 90))
Stock-out Rate = DIVIDE([Out of Stock Product Count], [In Scope Product Count])
Headcount = SUM(FactHRMonthly[Headcount])
New Hires = SUM(FactHRMonthly[NewHires])
Exits = SUM(FactHRMonthly[Exits])
Attrition Rate = DIVIDE([Exits], [Average Headcount])
Average Tenure = AVERAGE(FactHRMonthly[AverageTenureYears])
Revenue per Employee = DIVIDE([Total Sales], [Headcount])
Profit per Employee = DIVIDE([Gross Profit], [Headcount])
Data Freshness = MAX(RefreshAudit[FinishedAt])
```

Supporting measures (define only when inventory cost and product scope are validated):

```DAX
Average Inventory Value = AVERAGE(FactInventorySnapshot[InventoryValue])
Out of Stock Product Count = CALCULATE(DISTINCTCOUNT(DimProduct[ProductKey]), FactInventorySnapshot[InventoryQuantity] <= 0)
In Scope Product Count = DISTINCTCOUNT(DimProduct[ProductKey])
Average Headcount = AVERAGE(FactHRMonthly[Headcount])
Sales Target = SUM(FactSalesTarget[TargetAmount])
Target Variance = [Total Sales] - [Sales Target]
Target Achievement Percentage = DIVIDE([Total Sales], [Sales Target])
```

Target, inventory value, refresh-audit import and HR measures become active only after the indicated table exists and its grain is validated. Do not create blank fake facts just to make measures compile; remove/comment those measures until source deployment. `Inventory Turnover` should compare annualized COGS with average inventory value over a matching period. `Days of Supply` above uses a fixed 90-day demand window and should be implemented with a dedicated trailing-demand measure in the finished report. Averages over monthly headcount must be weighted by period length for multi-period analysis.

| Measure | Business definition | Grain / notes |
|---|---|---|
| Total Sales | Sum line sales amount | Filter context; internet channel |
| Total Cost | Product cost on sold lines | Not operating expense |
| Gross Profit / Margin | Revenue less product cost; divided by revenue | Gross proxy only |
| Total Orders / Quantity | Distinct order IDs / sold units | Orders can contain multiple lines |
| Average Order Value | Revenue per distinct order | Current filter context |
| YTD / prior year / growth | Calendar-to-date and comparable prior-year sales | Requires complete date dimension |
| MoM growth | Current versus prior month | Blank if prior month absent/zero |
| Rolling averages | Mean monthly revenue in last 3/12 months | Calendar month averages; partial current month included |
| Inventory | Current filtered stock snapshot | Snapshot, not additive across dates |
| Attrition | Exits divided by average headcount | HR source required; definition must match HR policy |
| Data freshness | Latest completed successful refresh | Audit table must be imported/related |

SQL equivalents for sales, gross margin and month-over-month values are available in `sql/07_financial_analytics.sql`.
