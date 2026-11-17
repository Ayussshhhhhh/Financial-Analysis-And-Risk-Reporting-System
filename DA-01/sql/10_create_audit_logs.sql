USE EnterpriseBI;
GO
IF OBJECT_ID('audit.PipelineRun','U') IS NULL CREATE TABLE audit.PipelineRun(RunId bigint IDENTITY PRIMARY KEY, PipelineName sysname NOT NULL, StartedAt datetime2 NOT NULL, FinishedAt datetime2 NULL, Status varchar(20) NOT NULL, SourceName sysname NULL, RowsRead bigint NULL, RowsWritten bigint NULL, ErrorNumber int NULL, ErrorMessage nvarchar(2048) NULL);
GO
CREATE OR ALTER PROCEDURE audit.usp_RunRefresh @SourceDatabase sysname=N'AdventureWorksDW' AS
BEGIN
 SET NOCOUNT ON; DECLARE @id bigint,@started datetime2=SYSUTCDATETIME();
 INSERT audit.PipelineRun(PipelineName,StartedAt,Status,SourceName) VALUES('AdventureWorksDWRefresh',@started,'Running',@SourceDatabase); SET @id=SCOPE_IDENTITY();
 BEGIN TRY
  EXEC stg.usp_LoadFromAdventureWorksDW @SourceDatabase;
  EXEC audit.usp_RunQualityChecks;
  EXEC mart.usp_BuildCurated @SourceDatabase;
  UPDATE audit.PipelineRun SET FinishedAt=SYSUTCDATETIME(),Status='Succeeded',RowsRead=(SELECT COUNT_BIG(*) FROM stg.InternetSales),RowsWritten=(SELECT COUNT_BIG(*) FROM mart.FactSalesInternet) WHERE RunId=@id;
 END TRY BEGIN CATCH
  UPDATE audit.PipelineRun SET FinishedAt=SYSUTCDATETIME(),Status='Failed',ErrorNumber=ERROR_NUMBER(),ErrorMessage=ERROR_MESSAGE() WHERE RunId=@id; THROW;
 END CATCH
END;
GO
