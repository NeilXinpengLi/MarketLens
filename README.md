# MarketLens

A domain-driven market intelligence radar. Point it at an industry, and it crawls sources, extracts competitor and product signals, scores them, and surfaces a live dashboard with alerts and audit tasks.

The first domain pack covers the **US CO2/industrial gas market** — tracking competitors, beverage-grade product signals, and compliance alerts.

---

## Quick Start

**Requirements:** Python 3.11+

```powershell
cd D:\MarketLens
python -m pip install -e .[dev]
.\scripts\reset_demo.ps1       # seeds database from local fixtures (fully offline)
.\scripts\serve.ps1            # starts dashboard on http://127.0.0.1:8021
```

Open **http://127.0.0.1:8021/?domain=co2_us_market**

---

## What It Does

1. **Crawl** — loads fixture pages (offline) or fetches live seed URLs
2. **Extract** — matches keyword signals from `domains/{domain}/keywords.yaml`
3. **Score** — weights signals using `domains/{domain}/scoring.yaml`
4. **Audit** — generates review tasks using `domains/{domain}/audit_rules.yaml`
5. **Dashboard** — FastAPI app showing competitors, alerts, and audit tasks

---

## Project Structure

```
domains/co2_us_market/     # domain pack (keywords, scoring, audit rules, fixtures)
app/jobs/                  # pipeline steps (crawl, extract, score, audit, knowledge)
app/api/                   # FastAPI dashboard + JSON API
app/core/                  # database models, session management
scripts/                   # PowerShell helpers
data/                      # SQLite database (created on first run)
```

---

## API

```
GET /api/domains/co2_us_market/summary
GET /api/domains/co2_us_market/competitors?min_score=70
GET /api/domains/co2_us_market/products
GET /api/domains/co2_us_market/alerts?severity=high
GET /api/domains/co2_us_market/audit-tasks?status=pending
```

Interactive API docs: **http://127.0.0.1:8021/docs**

---

## Running the Pipeline Manually

```powershell
# Offline demo (uses local fixture pages)
python -m app.jobs.run_pipeline --domain co2_us_market --mode reset-demo

# Live crawl (fetches real seed URLs)
python -m app.jobs.run_pipeline --domain co2_us_market --mode demo-live --live-limit 10
```

---

## Adding a New Domain

1. Create `domains/{your_domain}/` with `keywords.yaml`, `scoring.yaml`, and `audit_rules.yaml`
2. Add fixture pages to `domains/{your_domain}/fixtures/websites/pages.json`
3. Run `python -m app.jobs.run_pipeline --domain {your_domain} --mode reset-demo`

---

## Tech Stack

- **Python 3.11** — pipeline and API
- **FastAPI + Uvicorn** — dashboard and REST API
- **SQLAlchemy 2 + SQLite** — storage (PostgreSQL supported via `DATABASE_URL`)
- **Alembic** — database migrations
- **PyYAML** — domain pack configuration
