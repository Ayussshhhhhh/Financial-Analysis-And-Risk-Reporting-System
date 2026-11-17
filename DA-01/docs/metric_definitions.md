# Metric definitions

| Metric | Definition | Grain / filter | SQL / DAX | Owner | Limits |
|---|---|---|---|---|---|
| Revenue | Sum internet sales line SalesAmount | Order line; all report filters | `SUM(SalesAmount)` / `[Total Sales]` | Sales Finance | Single channel unless reseller fact added |
| Product cost | Sum TotalProductCost | Order line | `SUM(TotalProductCost)` / `[Total Cost]` | Finance | Not operating expense |
| Gross profit | Revenue less product cost | Order line aggregation | SQL view / `[Gross Profit]` | Finance | Not net or operating profit |
| Gross margin % | Gross profit / revenue | Current filter context | SQL view / `[Gross Margin Percentage]` | Finance | Blank when revenue is zero |
| Orders | Distinct SalesOrderNumber | Current filter context | `COUNT(DISTINCT)` / `[Total Orders]` | Sales | Sales order grain |
| AOV | Revenue / distinct orders | Current filter context | — / `[Average Order Value]` | Sales | Blank with no orders |
| YoY growth | Current period less same period prior year; percentage divided by prior value | Calendar period | Windowed SQL monthly equivalent / DAX time intelligence | Finance | Requires full date dimension |
| Inventory quantity | On-hand units at selected snapshot | Product-date | Snapshot sum / `[Inventory Quantity]` | Supply chain | Do not sum across snapshot dates |
| Days of supply | On hand divided by trailing daily demand | Product and snapshot | `vw_InventoryRisk` | Supply chain | 90-day proxy; zero demand yields null |
| Attrition rate | Exits / average headcount per HR-defined convention | Month/department/region | `DIVIDE([Exits],[Average Headcount])` | HR | Not populated without approved HR events |
| Data freshness | Latest successful completion timestamp | Refresh run | `audit.PipelineRun` | Data Engineering | Must exclude failed/in-progress runs |

Finance targets, operating profit, currency conversion, workforce costs, turnover, and inventory value require valid source facts and definitions. They are intentionally not inferred from unrelated sample columns.
