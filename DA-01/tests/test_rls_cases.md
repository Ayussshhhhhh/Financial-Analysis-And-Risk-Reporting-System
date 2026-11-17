# RLS and report acceptance cases

| Case | Action | Expected |
|---|---|---|
| North America manager | View as sample principal; select all regions and export/drill through | Only NA group rows in every connected fact |
| Europe manager | View as Europe identity | Europe only, no Pacific/NA detail |
| Pacific manager | View as Pacific identity | Pacific only |
| Unmapped identity | View as unknown user | No rows |
| CEO | View as executive | All approved groups |
| HR user | Open HR app and attempt sales detail URL/table | HR model only; no sales fact/model permission |
| Regional manager | Try changing slicer, URL filters, drill-through and Analyze in Excel | Other-region values remain inaccessible; export/build disabled unless approved |
| Refresh failure | Force a controlled source/credential failure in non-production | Failed audit row and scheduler/Service notification; prior published data remains clearly timestamped |
| Visual reconciliation | Compare card and month/category matrix totals to SQL view | Exact to display rounding under identical filters |

Capture actual screenshots in an authorized environment and record tester/date/build. This checklist itself is not evidence of a completed Power BI role test.
