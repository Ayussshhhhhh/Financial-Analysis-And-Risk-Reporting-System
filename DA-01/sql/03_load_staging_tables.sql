USE EnterpriseBI;
GO
/* Full idempotent reload from AdventureWorksDW. For large installations, replace with CDC/watermark extraction. */
CREATE OR ALTER PROCEDURE stg.usp_LoadFromAdventureWorksDW @SourceDatabase sysname=N'AdventureWorksDW' AS
BEGIN
 SET NOCOUNT ON; SET XACT_ABORT ON;
 DECLARE @sql nvarchar(max);
 IF DB_ID(@SourceDatabase) IS NULL THROW 51000,'Source AdventureWorksDW database not found.',1;
 BEGIN TRY
  BEGIN TRAN;
  TRUNCATE TABLE stg.InternetSales;
  SET @sql=N'INSERT stg.InternetSales(SalesOrderNumber,SalesOrderLineNumber,OrderDateKey,DueDateKey,ShipDateKey,CustomerKey,ProductKey,PromotionKey,CurrencyKey,SalesTerritoryKey,OrderQuantity,UnitPrice,ExtendedAmount,ProductStandardCost,TotalProductCost,SalesAmount,TaxAmt,Freight)
  SELECT SalesOrderNumber,SalesOrderLineNumber,OrderDateKey,DueDateKey,ShipDateKey,CustomerKey,ProductKey,PromotionKey,CurrencyKey,SalesTerritoryKey,OrderQuantity,UnitPrice,ExtendedAmount,ProductStandardCost,TotalProductCost,SalesAmount,TaxAmt,Freight FROM '+QUOTENAME(@SourceDatabase)+N'.dbo.FactInternetSales;';
  EXEC sys.sp_executesql @sql;
  TRUNCATE TABLE stg.InventorySnapshot;
  SET @sql=N'IF OBJECT_ID(N'''+QUOTENAME(@SourceDatabase)+N'.dbo.FactProductInventory'',N''U'') IS NOT NULL INSERT EnterpriseBI.stg.InventorySnapshot(DateKey,ProductKey,InventoryQuantity) SELECT DateKey,ProductKey,UnitsBalance FROM '+QUOTENAME(@SourceDatabase)+N'.dbo.FactProductInventory;';
  EXEC sys.sp_executesql @sql;
  COMMIT;
 END TRY BEGIN CATCH IF @@TRANCOUNT>0 ROLLBACK; THROW; END CATCH
END;
GO
/* Execute after restoring source: EXEC stg.usp_LoadFromAdventureWorksDW; */
