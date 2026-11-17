USE EnterpriseBI;
GO
CREATE OR ALTER VIEW mart.vw_InventoryRisk AS
WITH Latest AS (SELECT MAX(DateKey) DateKey FROM mart.FactInventorySnapshot), RecentDemand AS (
 SELECT ProductKey,SUM(OrderQuantity) Qty90 FROM mart.FactSalesInternet f JOIN mart.DimDate d ON d.DateKey=f.OrderDateKey CROSS JOIN Latest l
 WHERE d.FullDate >= DATEADD(day,-90,(SELECT FullDate FROM mart.DimDate WHERE DateKey=l.DateKey)) GROUP BY ProductKey)
SELECT d.FullDate SnapshotDate,p.ProductKey,p.ProductName,i.InventoryQuantity,COALESCE(rd.Qty90,0) UnitsSold90,
 CASE WHEN COALESCE(rd.Qty90,0)=0 THEN NULL ELSE i.InventoryQuantity/(rd.Qty90/90.0) END DaysOfSupply,
 CASE WHEN i.InventoryQuantity<=0 THEN 'Out of stock' WHEN COALESCE(rd.Qty90,0)>0 AND i.InventoryQuantity/(rd.Qty90/90.0)<14 THEN 'Low stock' ELSE 'Review' END RiskBand
FROM mart.FactInventorySnapshot i JOIN Latest l ON l.DateKey=i.DateKey JOIN mart.DimDate d ON d.DateKey=i.DateKey JOIN mart.DimProduct p ON p.ProductKey=i.ProductKey LEFT JOIN RecentDemand rd ON rd.ProductKey=i.ProductKey;
GO
