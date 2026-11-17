USE EnterpriseBI;
GO
IF OBJECT_ID('mart.DimDate','U') IS NULL CREATE TABLE mart.DimDate(DateKey int NOT NULL PRIMARY KEY, FullDate date NOT NULL, CalendarYear smallint NOT NULL, CalendarQuarter tinyint NOT NULL, MonthNumber tinyint NOT NULL, MonthName nvarchar(20) NOT NULL, YearMonth char(7) NOT NULL, IsWorkday bit NULL);
IF OBJECT_ID('mart.DimRegion','U') IS NULL CREATE TABLE mart.DimRegion(RegionKey int IDENTITY PRIMARY KEY, TerritoryKey int NOT NULL UNIQUE, RegionName nvarchar(50) NOT NULL, CountryRegionName nvarchar(50) NULL, GroupName nvarchar(50) NULL);
IF OBJECT_ID('mart.DimProduct','U') IS NULL CREATE TABLE mart.DimProduct(ProductKey int NOT NULL PRIMARY KEY, ProductName nvarchar(100) NOT NULL, ProductNumber nvarchar(25) NULL, SubcategoryName nvarchar(50) NULL, CategoryName nvarchar(50) NULL, StandardCost decimal(19,4) NULL, ListPrice decimal(19,4) NULL, IsCurrent bit NOT NULL DEFAULT 1);
IF OBJECT_ID('mart.FactSalesInternet','U') IS NULL CREATE TABLE mart.FactSalesInternet(
 SalesOrderNumber nvarchar(20) NOT NULL, SalesOrderLineNumber smallint NOT NULL, OrderDateKey int NOT NULL,
 CustomerKey int NOT NULL, ProductKey int NOT NULL, RegionKey int NULL, PromotionKey int NULL,
 CurrencyKey int NULL, OrderQuantity int NOT NULL, SalesAmount decimal(19,4) NOT NULL,
 TotalProductCost decimal(19,4) NULL, TaxAmt decimal(19,4) NULL, Freight decimal(19,4) NULL,
 CONSTRAINT PK_FactSalesInternet PRIMARY KEY(SalesOrderNumber,SalesOrderLineNumber),
 CONSTRAINT FK_Sales_Date FOREIGN KEY(OrderDateKey) REFERENCES mart.DimDate(DateKey),
 CONSTRAINT FK_Sales_Product FOREIGN KEY(ProductKey) REFERENCES mart.DimProduct(ProductKey),
 CONSTRAINT FK_Sales_Region FOREIGN KEY(RegionKey) REFERENCES mart.DimRegion(RegionKey));
IF OBJECT_ID('mart.FactInventorySnapshot','U') IS NULL CREATE TABLE mart.FactInventorySnapshot(DateKey int NOT NULL, ProductKey int NOT NULL, InventoryQuantity int NOT NULL, CONSTRAINT PK_FactInventory PRIMARY KEY(DateKey,ProductKey), CONSTRAINT FK_Inv_Date FOREIGN KEY(DateKey) REFERENCES mart.DimDate(DateKey), CONSTRAINT FK_Inv_Product FOREIGN KEY(ProductKey) REFERENCES mart.DimProduct(ProductKey));
GO
CREATE OR ALTER PROCEDURE mart.usp_BuildCurated @SourceDatabase sysname=N'AdventureWorksDW' AS
BEGIN
 SET NOCOUNT ON; SET XACT_ABORT ON;
 IF DB_ID(@SourceDatabase) IS NULL THROW 51001,'Source database not found.',1;
 DECLARE @sql nvarchar(max);
 BEGIN TRY
  BEGIN TRAN;
  TRUNCATE TABLE mart.FactSalesInternet; TRUNCATE TABLE mart.FactInventorySnapshot;
  IF OBJECT_ID('mart.FactHRMonthly','U') IS NOT NULL DELETE FROM mart.FactHRMonthly;
  DELETE FROM mart.DimProduct; DELETE FROM mart.DimRegion; DELETE FROM mart.DimDate;
  SET @sql=N'INSERT mart.DimDate(DateKey,FullDate,CalendarYear,CalendarQuarter,MonthNumber,MonthName,YearMonth,IsWorkday)
   SELECT DateKey,FullDateAlternateKey,CalendarYear,CalendarQuarter,MonthNumberOfYear,EnglishMonthName,CONVERT(char(7),FullDateAlternateKey,126),CASE WHEN DayNumberOfWeek IN(1,7) THEN 0 ELSE 1 END FROM '+QUOTENAME(@SourceDatabase)+N'.dbo.DimDate;'; EXEC sys.sp_executesql @sql;
  SET @sql=N'INSERT mart.DimRegion(TerritoryKey,RegionName,CountryRegionName,GroupName) SELECT SalesTerritoryKey,SalesTerritoryGroup,SalesTerritoryCountry,SalesTerritoryGroup FROM '+QUOTENAME(@SourceDatabase)+N'.dbo.DimSalesTerritory;'; EXEC sys.sp_executesql @sql;
  SET @sql=N'INSERT mart.DimProduct(ProductKey,ProductName,ProductNumber,SubcategoryName,CategoryName,StandardCost,ListPrice)
   SELECT p.ProductKey,p.EnglishProductName,p.ProductAlternateKey,sc.EnglishProductSubcategoryName,ca.EnglishProductCategoryName,p.StandardCost,p.ListPrice FROM '+QUOTENAME(@SourceDatabase)+N'.dbo.DimProduct p LEFT JOIN '+QUOTENAME(@SourceDatabase)+N'.dbo.DimProductSubcategory sc ON p.ProductSubcategoryKey=sc.ProductSubcategoryKey LEFT JOIN '+QUOTENAME(@SourceDatabase)+N'.dbo.DimProductCategory ca ON sc.ProductCategoryKey=ca.ProductCategoryKey;'; EXEC sys.sp_executesql @sql;
  INSERT mart.FactSalesInternet(SalesOrderNumber,SalesOrderLineNumber,OrderDateKey,CustomerKey,ProductKey,RegionKey,PromotionKey,CurrencyKey,OrderQuantity,SalesAmount,TotalProductCost,TaxAmt,Freight)
   SELECT s.SalesOrderNumber,s.SalesOrderLineNumber,s.OrderDateKey,s.CustomerKey,s.ProductKey,r.RegionKey,s.PromotionKey,s.CurrencyKey,s.OrderQuantity,s.SalesAmount,s.TotalProductCost,s.TaxAmt,s.Freight FROM stg.InternetSales s LEFT JOIN mart.DimRegion r ON r.TerritoryKey=s.SalesTerritoryKey;
  IF EXISTS(SELECT 1 FROM stg.InventorySnapshot) INSERT mart.FactInventorySnapshot SELECT DateKey,ProductKey,InventoryQuantity FROM stg.InventorySnapshot;
  COMMIT;
 END TRY BEGIN CATCH IF @@TRANCOUNT>0 ROLLBACK; THROW; END CATCH
END;
GO
IF NOT EXISTS(SELECT 1 FROM sys.indexes WHERE object_id=OBJECT_ID('mart.FactSalesInternet') AND name='IX_FactSalesInternet_DateRegion') CREATE INDEX IX_FactSalesInternet_DateRegion ON mart.FactSalesInternet(OrderDateKey,RegionKey) INCLUDE(SalesAmount,TotalProductCost,OrderQuantity);
GO
