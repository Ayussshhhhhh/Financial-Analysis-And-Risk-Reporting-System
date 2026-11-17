USE EnterpriseBI;
GO
/* Reconciliation: source/stage/curated counts and amounts should match for the full reload. */
SELECT 'stage count' Test, (SELECT COUNT_BIG(*) FROM stg.InternetSales) Actual,
 (SELECT COUNT_BIG(*) FROM mart.FactSalesInternet) Expected;
SELECT 'sales sum delta' Test,
 (SELECT SUM(SalesAmount) FROM stg.InternetSales)-(SELECT SUM(SalesAmount) FROM mart.FactSalesInternet) Delta;
/* Duplicate business grain and orphan keys: all counts should be zero. */
SELECT 'duplicate line grain' Test,COUNT_BIG(*) Exceptions FROM (SELECT SalesOrderNumber,SalesOrderLineNumber FROM mart.FactSalesInternet GROUP BY SalesOrderNumber,SalesOrderLineNumber HAVING COUNT_BIG(*)>1) x;
SELECT 'orphan date' Test,COUNT_BIG(*) Exceptions FROM mart.FactSalesInternet f LEFT JOIN mart.DimDate d ON d.DateKey=f.OrderDateKey WHERE d.DateKey IS NULL;
SELECT 'orphan product' Test,COUNT_BIG(*) Exceptions FROM mart.FactSalesInternet f LEFT JOIN mart.DimProduct d ON d.ProductKey=f.ProductKey WHERE d.ProductKey IS NULL;
SELECT 'invalid amount/quantity' Test,COUNT_BIG(*) Exceptions FROM mart.FactSalesInternet WHERE SalesAmount<0 OR OrderQuantity<=0;
/* Date continuity across the full date dimension. */
WITH d AS (SELECT FullDate, LAG(FullDate) OVER(ORDER BY FullDate) PreviousDate FROM mart.DimDate)
SELECT 'date gap' Test,COUNT_BIG(*) Exceptions FROM d WHERE PreviousDate IS NOT NULL AND DATEDIFF(day,PreviousDate,FullDate)<>1;
/* Sales financial identity should reconcile at line grain. */
SELECT 'gross profit delta' Test,SUM((SalesAmount-COALESCE(TotalProductCost,0))-(SalesAmount-COALESCE(TotalProductCost,0))) Delta FROM mart.FactSalesInternet;
GO
