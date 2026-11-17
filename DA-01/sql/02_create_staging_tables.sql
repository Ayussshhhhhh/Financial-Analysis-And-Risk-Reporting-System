USE EnterpriseBI;
GO
/* Stage tables are deliberately typed and limited to columns used by this model. */
IF OBJECT_ID('stg.InternetSales','U') IS NULL CREATE TABLE stg.InternetSales(
 SalesOrderNumber nvarchar(20) NOT NULL, SalesOrderLineNumber smallint NOT NULL,
 OrderDateKey int NOT NULL, DueDateKey int NULL, ShipDateKey int NULL,
 CustomerKey int NOT NULL, ProductKey int NOT NULL, PromotionKey int NULL,
 CurrencyKey int NULL, SalesTerritoryKey int NULL, OrderQuantity int NOT NULL,
 UnitPrice decimal(19,4) NULL, ExtendedAmount decimal(19,4) NULL,
 ProductStandardCost decimal(19,4) NULL, TotalProductCost decimal(19,4) NULL,
 SalesAmount decimal(19,4) NOT NULL, TaxAmt decimal(19,4) NULL, Freight decimal(19,4) NULL,
 LoadDtm datetime2 NOT NULL CONSTRAINT DF_StageInternet_Load DEFAULT SYSUTCDATETIME() /* no PK here: duplicates must land so quality validation can report them */);
IF OBJECT_ID('stg.InventorySnapshot','U') IS NULL CREATE TABLE stg.InventorySnapshot(
 DateKey int NOT NULL, ProductKey int NOT NULL, InventoryQuantity int NOT NULL,
 LoadDtm datetime2 NOT NULL CONSTRAINT DF_StageInventory_Load DEFAULT SYSUTCDATETIME(),
 CONSTRAINT PK_StageInventory PRIMARY KEY(DateKey,ProductKey));
IF OBJECT_ID('stg.LoadWatermark','U') IS NULL CREATE TABLE stg.LoadWatermark(
 SourceName sysname PRIMARY KEY, LastLoadedAt datetime2 NULL, LastDateKey int NULL);
GO
