# Power Query transformations

## Connection and folding
Connect to the `EnterpriseBI` database with the SQL Server connector and choose Import for this sample's moderate volume. Use the native database tables/views below. Keep filters and column selection in the SQL source steps so they fold; check **View Native Query** after each transformation. Do not use `Table.Buffer` on source tables. Credentials belong in Power BI's credential store, never in M text.

## Query inventory
Load `FactSalesInternet`, `FactInventorySnapshot`, `DimDate`, `DimRegion`, and `DimProduct`. Disable load for staging and helper queries. The source currently lacks populated HR, budget, or finance facts, so do not create fake query rows for those domains. If later approved sources exist, use `mart.FactHRMonthly` and corresponding approved curated finance tables.

Create a blank query for each template below. Change server/database values in Power BI parameters `pServer` and `pDatabase`.

```powerquery
// FactSalesInternet
let
    Source = Sql.Database(pServer, pDatabase),
    Sales = Source{[Schema="mart",Item="FactSalesInternet"]}[Data],
    Keep = Table.SelectColumns(Sales,{"SalesOrderNumber","SalesOrderLineNumber","OrderDateKey","CustomerKey","ProductKey","RegionKey","PromotionKey","CurrencyKey","OrderQuantity","SalesAmount","TotalProductCost"}),
    Types = Table.TransformColumnTypes(Keep,{{"OrderDateKey",Int64.Type},{"OrderQuantity",Int64.Type},{"SalesAmount",Currency.Type},{"TotalProductCost",Currency.Type}}),
    NullCost = Table.ReplaceValue(Types,null,0,Replacer.ReplaceValue,{"TotalProductCost"}),
    CleanKeys = Table.SelectRows(NullCost, each [SalesOrderNumber] <> null and [ProductKey] <> null)
in
    CleanKeys
```

```powerquery
// DimDate: date is a true date type; YearMonth remains a label for display.
let Source=Sql.Database(pServer,pDatabase), T=Source{[Schema="mart",Item="DimDate"]}[Data],
    Types=Table.TransformColumnTypes(T,{{"FullDate", type date},{"CalendarYear",Int64.Type},{"MonthNumber",Int64.Type},{"YearMonth",type text}}),
    Unique=Table.Distinct(Types,{"DateKey"}) in Unique
```

```powerquery
// DimProduct and DimRegion use curated product hierarchy and territory mapping.
let Source=Sql.Database(pServer,pDatabase), T=Source{[Schema="mart",Item="DimProduct"]}[Data],
    Types=Table.TransformColumnTypes(T,{{"ProductKey",Int64.Type},{"StandardCost",Currency.Type},{"ListPrice",Currency.Type}}),
    Labels=Table.TransformColumns(Types,{{"CategoryName", each if _=null then "Uncategorized" else Text.Trim(_), type text}})
in Labels
```

Use the same `Sql.Database` source and explicit `Table.SelectColumns`/types for `DimRegion` and `FactInventorySnapshot`. Customer and employee dimensions should only be added after a privacy review; select surrogate keys and approved aggregate attributes only. For source-side deduplication, preserve the declared fact grain and quarantine duplicate keys instead of silently choosing a row. SQL constraints currently enforce sales and snapshot grains.

## Documented transformations

| Query | Transformations | Null/error behavior |
|---|---|---|
| Sales fact | Explicit columns, integer keys/quantity, currency amounts, retain declared order-line grain | Missing cost treated as zero only in gross-profit calculation; missing keys filtered and surfaced in SQL QA |
| Date | Date and integer types; year-month label | Date key must be unique; gaps flagged by tests |
| Product | Hierarchy selected upstream; normalized missing category label | Missing category shown as Uncategorized |
| Region | Territory to group mapping in SQL | Unknown territory remains null and is a quality exception |
| Inventory | Integer snapshot grain | No inventory fact when source table is absent |
| HR/Finance | Not loaded absent approved source | No synthetic sensitive or monetary facts |

The AdventureWorksDW model supplies date, product, and territory dimensions. Customer-level detail can be joined by CustomerKey in a dedicated authorized report; default executive pages aggregate customer results.
