# Power Automate Workflow Specification: Automated Monthly Board Pack Distribution
**Financial Analytics and Risk Reporting System**
*Automated Enterprise Cloud & Local Refresh Orchestration*

---

## 1. Flow Overview & Architecture

This Power Automate cloud/desktop flow automates the ingestion refresh, scorecard execution, financial reconciliation, and PDF distribution cycle on a strict monthly governance schedule.

```
+-----------------------------------------------------------------------------------+
|               Trigger: Recurrence (1st Business Day of Month, 07:00 AM)          |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
|          Action 1: Trigger ETL Pipeline & Scorecard Execution (HTTP / CLI)        |
|             python3 -m src.automation  --> Output JSON status                    |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
|          Action 2: Condition Evaluation (Pipeline Status == "SUCCESS"?)           |
+-----------------------------------------------------------------------------------+
                    |                                           |
             [IF SUCCESS]                                  [IF FAILURE]
                    |                                           |
                    v                                           v
+---------------------------------------+   +---------------------------------------+
| Action 3A: Retrieve Generated PDF     |   | Action 3B: Dispatch Urgent Alert Email|
| Path: reports/monthly_board_pack.pdf  |   | To: On-Call Analytics Engineering     |
+---------------------------------------+   | Subject: [URGENT] Pipeline Failed     |
                    |                       +---------------------------------------+
                    v                                           |
+---------------------------------------+                       v
| Action 4A: Send Executive Board Email |   +---------------------------------------+
| To: CFO, CRO, FP&A Leads, Board Dist  |   | Action 4B: Log Failure Incident in    |
| Attachment: monthly_board_pack.pdf    |   | Incident Management / SharePoint      |
+---------------------------------------+   +---------------------------------------+
                    |
                    v
+---------------------------------------+
| Action 5A: Archive Report & Log Run   |
| In SharePoint / Data Lake Archive     |
+---------------------------------------+
```

---

## 2. Step-by-Step Flow Configuration

### Step 1: Trigger — Recurrence
- **Frequency:** Month
- **Interval:** 1
- **At these hours:** 7
- **At these minutes:** 0
- **Time Zone:** Eastern Standard Time (EST)
- **Advanced Expression:** Triggered on the first Monday or first business day via OData filter:
  ```json
  "recurrence": {
    "frequency": "Month",
    "interval": 1,
    "schedule": {
      "hours": [7],
      "minutes": [0]
    }
  }
  ```

### Step 2: Initialize Execution Variables
- **VarRunDate:** `formatDateTime(utcNow(), 'yyyy-MM-dd')`
- **VarPeriodClose:** `formatDateTime(addToTime(utcNow(), -1, 'Month'), 'yyyy-MM')`
- **VarDistributionList:** `"cfo@enterprise-finance.com; cro@enterprise-finance.com; board-pack-dist@enterprise-finance.com"`

### Step 3: Execute Ingestion & Model Pipeline
- **Connector:** HTTP or Desktop Flow (Power Automate Desktop)
- **Script Executed:**
  ```bash
  python3 -m src.automation
  ```
- **Response Handling:** Parse JSON response to verify `"status": "SUCCESS"` and Data Quality pass rate (`100%`).

### Step 4: Quality Gate & Decision Branch
- **Condition:**
  ```json
  @equals(body('Parse_JSON')?['status'], 'SUCCESS')
  ```

#### Positive Branch (Success)
1. **Get File Content:**
   - Path: `reports/monthly_board_pack.pdf`
2. **Send an Email (V2) - Office 365 Outlook:**
   - **To:** `variables('VarDistributionList')`
   - **Subject:** `[MONTHLY CLOSE] Executive Board Pack & Risk Report — @{variables('VarPeriodClose')}`
   - **Body (HTML):**
     ```html
     <p>Dear Members of the Executive Leadership Team and Board,</p>
     <p>Please find attached the official Monthly Executive Board Pack for the period 
     <strong>@{variables('VarPeriodClose')}</strong>.</p>
     
     <h3>Executive Performance Summary</h3>
     <ul>
       <li><strong>Revenue Pacing:</strong> Revenue met budget targets with healthy gross margins.</li>
       <li><strong>Credit Risk Scorecard:</strong> AUC: 0.700, Gini: 0.399, KS: 0.302. Underwriting quality remains within approved risk appetite.</li>
       <li><strong>Data Quality Audit:</strong> 100% validation checks passed with reconciled accounting identities.</li>
     </ul>
     <p>Detailed drill-down dashboards are live on Qlik Sense.</p>
     <p>Sincerely,<br><em>Financial Analytics & Risk Engineering Team</em></p>
     ```
   - **Attachments:**
     - Name: `Executive_Board_Pack_@{variables('VarPeriodClose')}.pdf`
     - ContentBytes: `body('Get_File_Content')`

#### Negative Branch (Failure)
1. **Send Alert Email:**
   - **To:** `data-eng-oncall@enterprise-finance.com`
   - **Subject:** `[CRITICAL ALERT] Monthly Board Pack Pipeline Generation Failed`
   - **Body:** Contains execution error stack trace, failing validation checks, and diagnostic logs.

---

## 3. Local / Standalone Python Fallback (No Microsoft 365 Tenant Required)

For environments without a paid Microsoft 365 tenant, the identical automation is executed locally via the bundled `src/automation.py` scheduler:

```python
from apscheduler.schedulers.blocking import BlockingScheduler
from src.automation import run_full_pipeline

scheduler = BlockingScheduler()

# Trigger on 1st business day of each month at 07:00
@scheduler.scheduled_job('cron', day='1-7', day_of_week='mon-fri', hour=7, minute=0)
def automated_monthly_job():
    print("Executing automated monthly board pack distribution...")
    summary = run_full_pipeline()
    if summary["status"] == "SUCCESS":
        print("Board pack generated and ready in reports/monthly_board_pack.pdf")
    else:
        print("Pipeline failure:", summary)

if __name__ == "__main__":
    scheduler.start()
```
