# Nexvia Technology Internship Projects

This repository contains the two internship deliverables, organized by project code for technical evaluation.

| Folder | Project | Focus |
|---|---|---|
| [`DA-04/`](DA-04/) | Financial Analysis and Risk Reporting System | Financial analytics, credit risk modeling, reporting automation |
| [`DA-01/`](DA-01/) | Enterprise Business Intelligence Suite | Multi-region enterprise BI, dimensional modeling, Power BI and Azure Data Factory |

## DA-04 — Financial Analysis and Risk Reporting System

### Architecture

The Python pipeline ingests lending and general-ledger data, validates and stages it, computes financial and credit-risk metrics, and produces reports and dashboard-ready outputs. SQL scripts build the curated SQLite model; notebooks document exploration, preparation, analysis, scorecard development, and validation. Reporting and automation modules generate Excel/PDF deliverables and coordinate pipeline execution.

Main components are in `DA-04/src/`, SQL transformations in `DA-04/sql/`, notebooks in `DA-04/notebooks/`, and generated or example reports in `DA-04/reports/` and `DA-04/data/reports/`.

### Setup and run

```bash
cd DA-04
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
python -m src.automation
```

Run the unit tests from `DA-04/` with `pytest tests/ -v`. See [`DA-04/README.md`](DA-04/README.md), [`DA-04/docs/system_guide.md`](DA-04/docs/system_guide.md), and [`DA-04/docs/architecture_diagram.md`](DA-04/docs/architecture_diagram.md) for details.

## DA-01 — Enterprise Business Intelligence Suite

### Architecture

The BI solution follows a warehouse workflow: SQL scripts create the database and staging tables, load and validate source data, and build a dimensional star schema. Further SQL modules implement financial, HR, supply-chain, security, and audit analytics. Power BI documentation describes the semantic model, DAX measures, dashboard specification, and row-level security. Azure Data Factory pipeline design is documented alongside the SQL implementation.

### Setup and run

This project is primarily a SQL and BI solution. Review `DA-01/docs/deployment_guide.md` for deployment context, then execute the scripts in `DA-01/sql/` in numeric order in a compatible SQL Server environment. Configure the Power BI model and data connections using the guides in `DA-01/power_bi/`; Azure Data Factory assets and setup notes are in `DA-01/azure_data_factory/`.

The Python validation test can be run from `DA-01/` after installing its dependencies:

```bash
cd DA-01
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
pytest -q
```

See [`DA-01/README.md`](DA-01/README.md), [`DA-01/docs/architecture.md`](DA-01/docs/architecture.md), and [`DA-01/docs/user_guide.md`](DA-01/docs/user_guide.md).

## Repository layout

```text
.
├── DA-01/   Enterprise Business Intelligence Suite
└── DA-04/   Financial Analysis and Risk Reporting System
```

Each project retains its own documentation, source, tests, configuration, and project-level README. The projects have separate dependency files; install dependencies from the relevant folder.

## Internship

Projects completed as part of the internship at Nexvia Technology.
