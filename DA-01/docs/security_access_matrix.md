# Access matrix

| Role | Regions | Sales | Finance | HR | Supply chain | Drill-through | Export |
|---|---|---|---|---|---|---|---|
| CEO / Executive | All approved | Aggregate + approved detail | All approved | Aggregates | All approved | Approved pages | Disabled by default; approve per workspace |
| CFO / Finance | All | Finance-required aggregates | Full financial model | None | None | Finance detail | Controlled |
| Regional Sales Manager | Assigned region | Own region | Margin measures approved for role | None | Regional risk only if attributed | Own-region detail | Controlled |
| HR Manager | All/approved regions | None | Workforce cost only if approved | Aggregates and approved HR detail | None | HR pages only | Controlled |
| Supply Chain | Assigned operating scope | Product demand aggregates | None | None | Inventory and fulfillment | Supply-chain detail | Controlled |
| Data Analyst | Explicit grant | Authorized datasets | Explicit grant | Explicit grant | Explicit grant | Authorized tables | Disabled unless approved |

Use separate semantic models/workspaces for Sales, Finance, HR, and Supply Chain because RLS is not column/table security. SQL permissions should grant only required schemas. Power BI workspace access uses least privilege; consumers receive app access, not Member/Contributor. Do not expose salary, national ID, date of birth, personal address, or personal contact data. Sample emails are non-routable examples.
