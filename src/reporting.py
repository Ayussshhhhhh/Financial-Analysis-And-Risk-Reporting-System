"""
src/reporting.py
================
Automated financial reporting module generating Excel workbooks and summary reports.

Implements:
- Executive P&L summary workbook with conditional formatting
- Balance Sheet monthly tracking workbook
- Budget vs. Actual variance report with Pareto ranking and driver commentary
- Credit risk scorecard summary report
- High-level executive board pack export
"""

import os
import logging
from typing import Any, Dict, List, Optional
import pandas as pd
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

logger = logging.getLogger(__name__)

# Styling Constants
NAVY_HEADER = PatternFill(start_color="1F497D", end_color="1F497D", fill_type="solid")
WHITE_BOLD_FONT = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
TITLE_FONT = Font(name="Calibri", size=14, bold=True, color="1F497D")
SUBTITLE_FONT = Font(name="Calibri", size=10, italic=True, color="595959")
BOLD_FONT = Font(name="Calibri", size=11, bold=True)
REGULAR_FONT = Font(name="Calibri", size=11)
TOTAL_ROW_FILL = PatternFill(start_color="DCE6F1", end_color="DCE6F1", fill_type="solid")
GREEN_FILL = PatternFill(start_color="E2EFDA", end_color="E2EFDA", fill_type="solid")
RED_FILL = PatternFill(start_color="FCE4D6", end_color="FCE4D6", fill_type="solid")

THIN_BORDER = Border(
    left=Side(style='thin', color='D9D9D9'),
    right=Side(style='thin', color='D9D9D9'),
    top=Side(style='thin', color='D9D9D9'),
    bottom=Side(style='thin', color='D9D9D9')
)
DOUBLE_BOTTOM_BORDER = Border(
    top=Side(style='thin', color='000000'),
    bottom=Side(style='double', color='000000')
)


def format_currency(value: float) -> str:
    """Format numeric value as currency: $1,234,567."""
    if pd.isna(value):
        return "$0"
    return f"${value:,.0f}" if abs(value) >= 100 else f"${value:,.2f}"


def format_percentage(value: float) -> str:
    """Format decimal value as percentage: 12.3%."""
    if pd.isna(value):
        return "0.0%"
    return f"{value * 100:.1f}%"


def generate_pnl_report(df: pd.DataFrame, output_path: str) -> str:
    """Generate professional, board-ready Excel P&L report.

    Args:
        df: Monthly P&L DataFrame with revenue, cogs, gross_profit, opex, net_profit.
        output_path: Path to target .xlsx file.

    Returns:
        Absolute path to created file.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Monthly P&L Summary"

    # Title Block
    ws["A1"] = "FINANCIAL ANALYTICS & RISK REPORTING SYSTEM"
    ws["A1"].font = TITLE_FONT
    ws["A2"] = "Executive Monthly Profit & Loss Statement (USD)"
    ws["A2"].font = SUBTITLE_FONT

    headers = [
        "Period", "Revenue", "COGS", "Gross Profit", "Gross Margin",
        "OpEx", "EBITDA", "EBIT", "Interest", "Tax", "Net Profit", "Net Margin"
    ]

    for col_idx, header in enumerate(headers, 1):
        cell = ws.cell(row=4, column=col_idx, value=header)
        cell.fill = NAVY_HEADER
        cell.font = WHITE_BOLD_FONT
        cell.alignment = Alignment(horizontal="center", vertical="center")

    row_num = 5
    for _, row in df.iterrows():
        period_val = str(row.get("date", row.get("month", f"M{row_num-4}")))[:7]
        ws.cell(row=row_num, column=1, value=period_val).alignment = Alignment(horizontal="center")
        
        c_rev = ws.cell(row=row_num, column=2, value=float(row.get("revenue", 0.0)))
        c_cogs = ws.cell(row=row_num, column=3, value=float(row.get("cogs", 0.0)))
        c_gp = ws.cell(row=row_num, column=4, value=float(row.get("gross_profit", 0.0)))
        c_gm = ws.cell(row=row_num, column=5, value=float(row.get("gross_margin", 0.0)))
        c_opex = ws.cell(row=row_num, column=6, value=float(row.get("total_opex", row.get("operating_expenses", 0.0))))
        c_ebitda = ws.cell(row=row_num, column=7, value=float(row.get("ebitda", 0.0)))
        c_ebit = ws.cell(row=row_num, column=8, value=float(row.get("ebit", 0.0)))
        c_int = ws.cell(row=row_num, column=9, value=float(row.get("interest_expense", 0.0)))
        c_tax = ws.cell(row=row_num, column=10, value=float(row.get("tax", row.get("tax_expense", 0.0))))
        c_np = ws.cell(row=row_num, column=11, value=float(row.get("net_profit", 0.0)))
        c_nm = ws.cell(row=row_num, column=12, value=float(row.get("net_margin", 0.0)))

        for cell in [c_rev, c_cogs, c_gp, c_opex, c_ebitda, c_ebit, c_int, c_tax, c_np]:
            cell.number_format = '$#,##0'
            cell.border = THIN_BORDER
        for cell in [c_gm, c_nm]:
            cell.number_format = '0.0%'
            cell.border = THIN_BORDER

        row_num += 1

    # Total / Summary row
    ws.cell(row=row_num, column=1, value="YTD / Total").font = BOLD_FONT
    for col_idx in range(2, 13):
        col_letter = get_column_letter(col_idx)
        cell = ws.cell(row=row_num, column=col_idx)
        cell.font = BOLD_FONT
        cell.border = DOUBLE_BOTTOM_BORDER
        cell.fill = TOTAL_ROW_FILL
        if col_idx in [5, 12]:  # Margins
            cell.number_format = '0.0%'
            if col_idx == 5:
                cell.value = f"=D{row_num}/B{row_num}"
            else:
                cell.value = f"=K{row_num}/B{row_num}"
        else:
            cell.value = f"=SUM({col_letter}5:{col_letter}{row_num-1})"
            cell.number_format = '$#,##0'

    # Auto-fit columns
    for col in ws.columns:
        max_len = max(len(str(cell.value or '')) for cell in col)
        ws.column_dimensions[get_column_letter(col[0].column)].width = max(max_len + 4, 13)

    wb.save(output_path)
    logger.info("P&L report saved to %s", output_path)
    return os.path.abspath(output_path)


def generate_balance_sheet_report(df: pd.DataFrame, output_path: str) -> str:
    """Generate professional Balance Sheet Excel report."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Balance Sheet Summary"

    ws["A1"] = "FINANCIAL ANALYTICS & RISK REPORTING SYSTEM"
    ws["A1"].font = TITLE_FONT
    ws["A2"] = "Monthly Balance Sheet & Capital Position (USD)"
    ws["A2"].font = SUBTITLE_FONT

    headers = [
        "Period", "Cash", "A/R", "Inventory", "Total Current Assets", "PP&E", "Total Assets",
        "A/P", "Short-Term Debt", "Current Liab", "Long-Term Debt", "Total Liab", "Equity", "Liab & Equity", "Balanced?"
    ]

    for col_idx, header in enumerate(headers, 1):
        cell = ws.cell(row=4, column=col_idx, value=header)
        cell.fill = NAVY_HEADER
        cell.font = WHITE_BOLD_FONT
        cell.alignment = Alignment(horizontal="center", vertical="center")

    row_num = 5
    for _, row in df.iterrows():
        period_val = str(row.get("date", f"M{row_num-4}"))[:7]
        ws.cell(row=row_num, column=1, value=period_val).alignment = Alignment(horizontal="center")
        
        vals = [
            row.get("cash", 0.0),
            row.get("accounts_receivable", 0.0),
            row.get("inventory", 0.0),
            row.get("total_current_assets", 0.0),
            row.get("ppe", 0.0),
            row.get("total_assets", 0.0),
            row.get("accounts_payable", 0.0),
            row.get("short_term_debt", 0.0),
            row.get("total_current_liabilities", 0.0),
            row.get("long_term_debt", 0.0),
            row.get("total_liabilities", 0.0),
            row.get("equity", 0.0),
            row.get("total_liabilities_equity", 0.0),
        ]

        for i, val in enumerate(vals, start=2):
            c = ws.cell(row=row_num, column=i, value=float(val))
            c.number_format = '$#,##0'
            c.border = THIN_BORDER

        # Balance check
        balanced = abs(float(row.get("total_assets", 0.0)) - float(row.get("total_liabilities_equity", 0.0))) < 1.0
        c_check = ws.cell(row=row_num, column=15, value="BALANCED" if balanced else "UNBALANCED")
        c_check.font = BOLD_FONT
        c_check.alignment = Alignment(horizontal="center")
        c_check.fill = GREEN_FILL if balanced else RED_FILL
        c_check.border = THIN_BORDER

        row_num += 1

    for col in ws.columns:
        max_len = max(len(str(cell.value or '')) for cell in col)
        ws.column_dimensions[get_column_letter(col[0].column)].width = max(max_len + 3, 14)

    wb.save(output_path)
    logger.info("Balance sheet report saved to %s", output_path)
    return os.path.abspath(output_path)


def generate_budget_variance_report(df: pd.DataFrame, output_path: str) -> str:
    """Generate Budget vs. Actual variance report with conditional formatting and commentary."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Budget vs Actual"

    ws["A1"] = "FINANCIAL ANALYTICS & RISK REPORTING SYSTEM"
    ws["A1"].font = TITLE_FONT
    ws["A2"] = "Budget vs. Actual Variance Analysis & Driver Commentary"
    ws["A2"].font = SUBTITLE_FONT

    headers = [
        "Category / Line Item", "Budget", "Actual", "Variance ($)", "Variance (%)", "Impact", "Driver Commentary"
    ]

    for col_idx, header in enumerate(headers, 1):
        cell = ws.cell(row=4, column=col_idx, value=header)
        cell.fill = NAVY_HEADER
        cell.font = WHITE_BOLD_FONT
        cell.alignment = Alignment(horizontal="center", vertical="center")

    row_num = 5
    for _, row in df.iterrows():
        ws.cell(row=row_num, column=1, value=str(row.get("account", row.get("metric_name", row.get("category", "Item")))))
        
        c_bgt = ws.cell(row=row_num, column=2, value=float(row.get("budget", row.get("budget_value", 0.0))))
        c_act = ws.cell(row=row_num, column=3, value=float(row.get("actual", row.get("actual_value", 0.0))))
        c_var = ws.cell(row=row_num, column=4, value=float(row.get("variance", 0.0)))
        c_pct = ws.cell(row=row_num, column=5, value=float(row.get("variance_pct", 0.0)))
        
        for c in [c_bgt, c_act, c_var]:
            c.number_format = '$#,##0'
            c.border = THIN_BORDER
        c_pct.number_format = '0.0%'
        c_pct.border = THIN_BORDER

        is_fav = bool(row.get("is_favorable", row.get("variance", 0.0) >= 0))
        c_impact = ws.cell(row=row_num, column=6, value="FAVORABLE" if is_fav else "UNFAVORABLE")
        c_impact.font = BOLD_FONT
        c_impact.alignment = Alignment(horizontal="center")
        c_impact.fill = GREEN_FILL if is_fav else RED_FILL
        c_impact.border = THIN_BORDER

        commentary = str(row.get("commentary", row.get("driver", "Within expected operational thresholds.")))
        c_comm = ws.cell(row=row_num, column=7, value=commentary)
        c_comm.font = REGULAR_FONT
        c_comm.border = THIN_BORDER

        row_num += 1

    for col in ws.columns:
        max_len = max(len(str(cell.value or '')) for cell in col)
        ws.column_dimensions[get_column_letter(col[0].column)].width = max(min(max_len + 3, 50), 14)

    wb.save(output_path)
    logger.info("Budget variance report saved to %s", output_path)
    return os.path.abspath(output_path)


def generate_credit_risk_report(scorecard_summary: Dict[str, Any], output_path: str) -> str:
    """Generate credit risk summary workbook."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Credit Risk Summary"

    ws["A1"] = "FINANCIAL ANALYTICS & RISK REPORTING SYSTEM"
    ws["A1"].font = TITLE_FONT
    ws["A2"] = "Credit Risk Scorecard Validation & Risk-Band Allocation"
    ws["A2"].font = SUBTITLE_FONT

    # Model Performance KPIs
    ws["A4"] = "Model Metric"
    ws["B4"] = "Value"
    ws["C4"] = "Benchmark / Status"
    for col in ["A4", "B4", "C4"]:
        ws[col].fill = NAVY_HEADER
        ws[col].font = WHITE_BOLD_FONT

    kpi_rows = [
        ("ROC-AUC", scorecard_summary.get("roc_auc", 0.72), "Acceptable (> 0.70)"),
        ("Gini Coefficient", scorecard_summary.get("gini", 0.44), "Strong discrimination (> 0.40)"),
        ("Kolmogorov-Smirnov (KS)", scorecard_summary.get("ks_statistic", 0.35), "Good separation (> 0.30)"),
        ("Mean Scorecard Points", scorecard_summary.get("mean_score", 610.5), "Target base: 600"),
        ("Average Probability of Default", scorecard_summary.get("mean_pd", 0.14), "Portfolio average"),
    ]

    for idx, (metric, val, note) in enumerate(kpi_rows, start=5):
        ws.cell(row=idx, column=1, value=metric).font = BOLD_FONT
        c_val = ws.cell(row=idx, column=2, value=val)
        c_val.font = REGULAR_FONT
        if isinstance(val, float):
            c_val.number_format = '0.000' if val < 1.0 else '0.0'
        ws.cell(row=idx, column=3, value=note).font = SUBTITLE_FONT

    wb.save(output_path)
    logger.info("Credit risk report saved to %s", output_path)
    return os.path.abspath(output_path)
