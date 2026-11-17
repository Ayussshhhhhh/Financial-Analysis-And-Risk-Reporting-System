# Architecture and data flow

```mermaid
flowchart LR
 S[AdventureWorksDW SQL Server] -->|full extract / future watermark| I[SQL Agent or ADF Copy]
 I --> T[EnterpriseBI stg schema]
 T --> Q[QA checks and audit]
 Q --> M[mart dimensions and facts]
 M --> P[Power Query / Power BI semantic models]
 U[Entra ID principals] --> R[Security map + workspace roles]
 R --> P
 P --> W[Power BI Service app/workspaces]
 W --> X[Executives, regional managers, domain teams]
 I --> A[Audit log and alerts]
```

Refresh flow: scheduled runner executes `audit.usp_RunRefresh`; staging and curated loads are transactional per procedure; failures are recorded and rethrown for scheduler notification; QA is reviewed before semantic model refresh. SQL Server Agent history plus `audit.PipelineRun` is the local monitoring path. ADF production version uses linked service, copy activity, stored procedure activity, failure branch, and monitor alerts.

Security flow: Entra ID authenticates user; Power BI workspace/app grants access to the relevant domain model; dynamic mapping filters regional data. Data model isolation provides domain boundaries that RLS alone cannot enforce.
