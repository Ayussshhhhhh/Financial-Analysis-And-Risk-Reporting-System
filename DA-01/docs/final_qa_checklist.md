# Final QA checklist

## Repository and source
- [x] Ordered SQL setup, staging, quality, curated model, security and analytics scripts included.
- [x] SQL source assumptions and unavailable services documented.
- [x] Power Query, semantic model and DAX specifications included.
- [x] Access matrix, data dictionary, metric definitions and user guide included.
- [x] Architecture diagram, editable presentation, talk track and reflection template included.
- [ ] Restore AdventureWorksDW and execute scripts 01–10 in a SQL Server instance.
- [ ] Resolve source-version differences and capture SQL reconciliation output.

## Model and security
- [ ] Build PBIX in Power BI Desktop and confirm query folding.
- [ ] Verify Date table, relationships, formats, and measures against SQL outputs.
- [ ] Test all dynamic RLS identities and unmapped user in Desktop and Service.
- [ ] Separate domain models/workspaces and verify export/build permissions.

## Automation and publication
- [ ] Configure SQL Agent or Task Scheduler using least privilege.
- [ ] Confirm audit success/failure records and alert delivery.
- [ ] Publish to approved workspace, set gateway/credentials and refresh schedule.
- [ ] Validate Service refresh history and region-limited app access.
- [ ] Capture real screenshots and test evidence; do not substitute design docs for execution evidence.

## Portfolio handoff
- [x] Python calculation tests run successfully in current environment.
- [ ] Produce source-backed executive/monthly performance review after reconciliation.
- [ ] Add real PBIX and screenshots only after creation in Power BI Desktop.
- [ ] Review generated report for data privacy and currency correctness.
