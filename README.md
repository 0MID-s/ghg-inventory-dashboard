# GHG Inventory Dashboard

A Streamlit web application simulating a full Scope 1/2/3 greenhouse gas emissions inventory for a mid-size organisation, with an interactive KPI dashboard and smart meter energy analytics. Built to demonstrate end-to-end competency in GHG accounting methodology, data engineering, and visual reporting.

---

## What It Does

**Emissions Overview tab**
- Scope 1/2/3 KPI cards with year-on-year delta
- Scope breakdown donut chart (proportional split across fleet, electricity, travel, supply chain)
- Monthly emissions trend (area-fill line chart, FY 2024)
- Emissions vs. 2030 net-zero target pathway (−45% reduction from base year)
- Downloadable emissions inventory CSV

**Smart Meter tab**
- Daily kWh consumption across three office meters (Office Floor 1, Floor 2, Server Room)
- Stacked area chart showing total and per-location consumption simultaneously
- 7-day rolling average smoothed trend
- Raw daily readings table with BEIS 2024 kWh → tCO₂e conversion details

---

## Skills Demonstrated

| Area | Detail |
|------|--------|
| GHG accounting | Scope 1/2/3 inventory under GHG Protocol Corporate Standard; operational control boundary; BEIS 2024 UK emission factors throughout |
| Smart meter processing | Daily kWh ingestion, aggregation, and CO₂e conversion (0.20493 kgCO₂e/kWh UK grid average) |
| Data engineering | Modular `src/` architecture — data loading, transformation, charting, and styling separated from the Streamlit entry point |
| Interactive visualisation | Plotly donut, area-fill, stacked, and bar+line overlay charts; hover tooltips; download button |
| Deployment | Streamlit Community Cloud with environment variable secrets management |

---

## Stack

| Component | Technology |
|-----------|------------|
| Language | Python 3.11 |
| Web framework | Streamlit |
| Visualisation | Plotly |
| Data processing | pandas |
| Secrets management | python-dotenv |

---

## Local Setup

```bash
# 1. Clone and enter the repo
git clone https://github.com/0MID-s/ghg-inventory-dashboard.git
cd ghg-inventory-dashboard

# 2. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate        # macOS / Linux
.venv\Scripts\activate           # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
streamlit run app.py
```

The dashboard opens at `http://localhost:8501`. No API keys are required — all data is bundled in `data/`.

---

## Streamlit Community Cloud Deployment

1. Fork or push this repo to your GitHub account
2. Go to [share.streamlit.io](https://share.streamlit.io) and click **New app**
3. Select this repository, set branch to `main`, and set **Main file path** to `app.py`
4. Click **Deploy** — no secrets are needed for this app

---

## Project Structure

```
ghg-inventory-dashboard/
├── app.py                  # Streamlit entry point (UI only)
├── requirements.txt
├── data/
│   ├── emissions.csv       # 96 monthly Scope 1/2/3 records (synthetic)
│   └── smart_meter.csv     # Daily kWh readings, 3 meters (synthetic)
└── src/
    ├── data_loader.py      # CSV ingestion with caching
    ├── metrics.py          # KPI computation (totals, YoY delta, tCO₂e)
    ├── charts.py           # Plotly figure factory functions
    └── styles.py           # CSS injection for custom theme
```

---

## Data Notes

All data is synthetic and does not represent any real organisation. The emissions dataset covers 96 monthly records across four categories — fleet vehicles (Scope 1), grid electricity (Scope 2), business travel and supply chain (Scope 3) — with BEIS 2024 emission factors applied throughout.
