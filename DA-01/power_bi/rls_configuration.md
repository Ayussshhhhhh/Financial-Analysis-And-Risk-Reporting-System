# Row-level security and access model

## Dynamic regional role
Import `sec.UserRegionRole` as `SecurityMap`; hide it from report view. Use this table filter expression as a dynamic gate on `DimRegion` (set model relationships to single direction; apply security filter in both directions only where needed to propagate region to facts):

```DAX
VAR Login = LOWER(USERPRINCIPALNAME())
VAR CurrentGroup = DimRegion[GroupName]
RETURN COUNTROWS(FILTER(SecurityMap,
    LOWER(SecurityMap[UserEmail]) = Login &&
    (SecurityMap[RoleName] = "Executive" ||
     (SecurityMap[RoleName] = "RegionalManager" && SecurityMap[RegionName] = CurrentGroup) ||
     SecurityMap[RoleName] IN {"Finance", "HR", "SupplyChain"}))) > 0
```

Assign users to the appropriate Power BI role. Use only sample `example.com` identities in source control. Add region group mappings from the actual restored dataset; never assume only three groups. Test with Desktop **View as** and actual Service test accounts. Empty user mapping should yield no rows.

## Important domain separation
RLS controls rows, not table/column permissions. A shared semantic model with RLS alone cannot guarantee HR users cannot query sales details or sales users cannot query HR facts. Publish separate domain semantic models/workspaces (Sales, Finance, HR, Supply Chain) with least-privilege workspace roles and omit unauthorized tables. Give executives access to approved combined aggregates. Disable Build and export permissions unless approved. Detailed transaction access requires explicit analyst authorization and audit controls.

## Test identities

| Identity | Expected scope |
|---|---|
| north.america.manager@example.com | Only territories whose group is North America |
| europe.manager@example.com | Only Europe group |
| pacific.manager@example.com | Only Pacific group |
| cfo@example.com | Finance workspace/model, all authorized regions |
| hr.manager@example.com | HR aggregate model only |
| supply.chain@example.com | Inventory model only |
| ceo@example.com | Executive approved cross-region model |
| unmapped@example.com | No rows |

Validate each query through each domain model; verify drill-through and export inherit the same boundary. See `tests/test_rls_cases.md`.
