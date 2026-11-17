# Test plan and current evidence

Automated calculation tests are implemented in `tests/test_data_quality.py` using only Python's standard library. SQL checks are in `tests/sql_validation_tests.sql`; they must be run against a restored AdventureWorksDW/EnterpriseBI instance. RLS and visual tests require Power BI Desktop/Service as detailed in `tests/test_rls_cases.md`.

| Test area | Automated artifact | Current status |
|---|---|---|
| Gross margin, YTD, YoY, rolling average, inventory days supply, attrition edge cases | Python unit tests | Executed in repository environment; results noted after run |
| Stage/curated reconciliation, duplicate grain, FK gaps, date continuity | SQL validation script | Not run: no SQL Server instance attached |
| Dynamic regional roles | Manual role matrix | Requires Desktop View as and Service identities |
| Dashboard accuracy and refresh failure | Manual acceptance cases | Requires Power BI and scheduler |

Never mark environment-dependent checks passed without execution evidence.
