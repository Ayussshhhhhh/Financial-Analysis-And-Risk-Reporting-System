# Local scheduled equivalent: SQL Server Agent

Create a SQL Server Agent job `EnterpriseBI_DailyRefresh` with a T-SQL step executed against `EnterpriseBI`:

```sql
EXEC audit.usp_RunRefresh @SourceDatabase = N'AdventureWorksDW';
```

Schedule after the source is available. Use a dedicated SQL Agent proxy/credential with execute permissions only on the required procedures and select access on source facts. Configure job failure notification to the operator through the organization's Database Mail setup. Add a second step to run `04_data_quality_checks.sql` or replace it with a stored procedure that `THROW`s when blocking exceptions are nonzero. Review `audit.PipelineRun` and Agent job history after runs. Do not put passwords in job command text.

For SQL Server Express without Agent, Windows Task Scheduler can invoke `sqlcmd` with integrated authentication under a restricted service account. Capture exit code and output in protected logs, alert on nonzero exit, and protect the script/log folder. The scheduler configuration is environment-specific and must be captured during actual setup.
