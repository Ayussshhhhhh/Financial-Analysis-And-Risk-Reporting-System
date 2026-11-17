/* HR is not fabricated: AdventureWorksDW employee attributes do not provide a dated hire/exit event fact.
   Obtain an approved HR source and aggregate it before loading. Never ingest salary, DOB, national ID,
   home address, or personal contact fields into the executive model. */
USE EnterpriseBI;
GO
IF OBJECT_ID('mart.FactHRMonthly','U') IS NULL CREATE TABLE mart.FactHRMonthly(
 MonthDateKey int NOT NULL, RegionKey int NULL, DepartmentName nvarchar(100) NOT NULL,
 Headcount int NOT NULL, NewHires int NOT NULL, Exits int NOT NULL, AverageTenureYears decimal(9,2) NULL,
 CONSTRAINT PK_FactHRMonthly PRIMARY KEY(MonthDateKey,RegionKey,DepartmentName),
 CONSTRAINT FK_HR_Date FOREIGN KEY(MonthDateKey) REFERENCES mart.DimDate(DateKey));
GO
