# Azure Data Factory production pipeline design

## Pipeline: `pl_enterprise_bi_daily`

| Order | Activity | Configuration |
|---|---|---|
| 1 | Lookup `GetWatermark` | Read last successful source watermark; default full load when absent |
| 2 | Copy `CopyInternetSales` | AdventureWorksDW `dbo.FactInternetSales` to SQL `EnterpriseBI.stg.InternetSales`; for current sample use full refresh |
| 3 | Copy `CopyInventory` | Optional `FactProductInventory` to `stg.InventorySnapshot`; skip when source object absent |
| 4 | Stored procedure `RunQualityChecks` | Execute quality validation; fail pipeline on blocking exceptions |
| 5 | Stored procedure `BuildCurated` | Execute `mart.usp_BuildCurated` |
| 6 | Stored procedure `RecordSuccess` | Update audit and committed watermark |
| Failure branch | `RecordFailure` + alert | Record error, send Azure Monitor action-group notification; do not advance watermark |

## Linked services and datasets

- `ls_awdw_sql`: SQL Server source; use self-hosted integration runtime for on-premises SQL, managed identity where supported for Azure SQL, and Key Vault secret reference where password auth is unavoidable.
- `ls_enterprisebi_sql`: destination SQL Server/Azure SQL.
- Parameterized source dataset: database, schema, table, optional modified-date column.
- Parameterized destination dataset: `stg` schema, destination table.
- Pipeline parameters: `pSourceDatabase`, `pLoadMode` (`Full` initially), `pRunDateUtc`, `pBatchId`.

## Schedule, retry, monitoring

Schedule daily after source load completion; use a fixed UTC window and timezone-aware business reporting labels. Retry transient network errors up to three times with exponential backoff; do not retry schema/quality failures. Set activity timeout based on measured volume. Enable secure input/output for credential-bearing activities. Send failed-run alerts through Monitor and retain run/audit history according to organizational policy. Validate source and destination counts and sales amount reconciliation before promoting.

## Incremental strategy

AdventureWorks sample can begin with full reload. For production, use Change Tracking/CDC or a reliable modified timestamp and a persisted committed watermark. Include deletes, late-arriving rows, and dimension updates; use idempotent merge keys and periodic full reconciliation. Never advance watermark before curated load and quality checks commit.

## Migration from local SQL Agent

Preserve stored procedures and audit schema, create ADF linked services/datasets, replace the Agent schedule with a trigger, execute the same procedures via Stored Procedure activities, map job failure to ADF failure branch, and configure Monitor alerts. Reconcile at least three consecutive runs before disabling the local scheduler. The design is implementation-ready but is not a live ADF deployment or exported resource from a tenant.
