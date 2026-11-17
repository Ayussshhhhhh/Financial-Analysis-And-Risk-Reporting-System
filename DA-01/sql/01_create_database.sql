/* Run once as a SQL Server administrator. Restore AdventureWorksDW separately. */
IF DB_ID(N'EnterpriseBI') IS NULL CREATE DATABASE EnterpriseBI;
GO
USE EnterpriseBI;
GO
IF NOT EXISTS(SELECT 1 FROM sys.schemas WHERE name='stg') EXEC('CREATE SCHEMA stg');
IF NOT EXISTS(SELECT 1 FROM sys.schemas WHERE name='mart') EXEC('CREATE SCHEMA mart');
IF NOT EXISTS(SELECT 1 FROM sys.schemas WHERE name='audit') EXEC('CREATE SCHEMA audit');
IF NOT EXISTS(SELECT 1 FROM sys.schemas WHERE name='sec') EXEC('CREATE SCHEMA sec');
GO
