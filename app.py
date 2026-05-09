"""GHG Inventory Dashboard — main entry point.
Architecture rule: only st.* calls, src/ imports, load_dotenv(). No business logic here.
"""
import streamlit as st
from dotenv import load_dotenv

from src.data_loader import load_emissions, load_smart_meter
from src.metrics import compute_kpis, compute_meter_kpis
from src.charts import scope_breakdown_chart, monthly_trend_chart, net_zero_pathway_chart, energy_stacked_chart, energy_rolling_chart
from src.styles import get_css

load_dotenv()

st.set_page_config(
    page_title="GHG Inventory Dashboard",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(get_css(), unsafe_allow_html=True)

# ── Header ─────────────────────────────────────────────────────────────────

st.markdown("""
<div style="padding:0.75rem 0 0.9rem 0; border-bottom:3px solid #009FE3; margin-bottom:1rem;">
  <h1 style="margin:0; font-size:1.8rem; font-weight:700; color:#003F87; line-height:1.2;">
    GHG Inventory Dashboard
  </h1>
  <div style="display:flex; gap:0.6rem; flex-wrap:wrap; margin-top:0.6rem;">
    <span style="background:#E8F3FC; color:#003F87; padding:3px 10px; border-radius:20px; font-size:0.72rem; font-weight:600; border:1px solid #CCE4F5;">FY 2024</span>
    <span style="background:#E8F3FC; color:#003F87; padding:3px 10px; border-radius:20px; font-size:0.72rem; font-weight:600; border:1px solid #CCE4F5;">GHG Protocol Corporate</span>
    <span style="background:#E8F3FC; color:#003F87; padding:3px 10px; border-radius:20px; font-size:0.72rem; font-weight:600; border:1px solid #CCE4F5;">BEIS 2024 UK Factors</span>
    <span style="background:#E8F3FC; color:#003F87; padding:3px 10px; border-radius:20px; font-size:0.72rem; font-weight:600; border:1px solid #CCE4F5;">Operational Control</span>
    <span style="background:#FFF4E0; color:#8A5000; padding:3px 10px; border-radius:20px; font-size:0.72rem; font-weight:600; border:1px solid #FFD580;">Synthetic Data</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Data loading (cached) ───────────────────────────────────────────────────

emissions_df = load_emissions()
meter_df = load_smart_meter()

# ── KPI computation ─────────────────────────────────────────────────────────

kpis = compute_kpis(emissions_df)
scope1 = kpis["scope_totals"].get("Scope 1", 0)
scope2 = kpis["scope_totals"].get("Scope 2", 0)
scope3 = kpis["scope_totals"].get("Scope 3", 0)
total = kpis["total_co2e"]

# ── Sidebar ─────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("""
<div style="padding-bottom:0.85rem; border-bottom:2px solid #CCE4F5; margin-bottom:0.85rem;">
  <p style="margin:0; font-size:0.62rem; letter-spacing:3px; text-transform:uppercase; color:#6B8CAE;">Project</p>
  <p style="margin:3px 0 0 0; font-size:1rem; font-weight:700; color:#003F87;">GHG Emissions Inventory</p>
</div>
""", unsafe_allow_html=True)

    st.markdown("**Reporting year:** FY 2024")
    st.markdown("**Standard:** GHG Protocol Corporate")
    st.markdown("**Emission factors:** BEIS 2024 UK")
    st.markdown("**Boundary:** Operational control")

    st.divider()

    st.markdown("**Scope totals**")
    for scope, s_total in sorted(kpis["scope_totals"].items()):
        pct = s_total / total * 100
        st.markdown(f"- {scope}: **{s_total:,.0f} tCO₂e** ({pct:.0f}%)")

    st.divider()

    st.metric(
        label="Total Portfolio Emissions",
        value=f"{total:,.0f} tCO₂e",
        delta=f"{kpis['yoy_pct']:+.1f}% YoY",
        delta_color="inverse",
    )

    st.divider()
    st.caption("Synthetic data — does not represent any real organisation.")

# ── Tab layout ──────────────────────────────────────────────────────────────

tab_overview, tab_meter = st.tabs(["Emissions Overview", "Smart Meter"])

# ── Overview Tab ────────────────────────────────────────────────────────────

with tab_overview:
    st.markdown("""
<div style="margin:0.25rem 0 0.8rem 0; padding:0.4rem 0.75rem; border-left:3px solid #009FE3; background:#F8FBFF; border-radius:0 4px 4px 0;">
  <p style="margin:0; font-size:0.62rem; letter-spacing:2px; text-transform:uppercase; color:#6B8CAE; font-weight:600;">Overview</p>
  <p style="margin:2px 0 0 0; font-size:1rem; font-weight:700; color:#003F87;">Portfolio Summary</p>
</div>
""", unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Total Emissions",
        f"{total:,.0f} tCO₂e",
        f"{kpis['yoy_pct']:+.1f}% vs prior year",
        delta_color="inverse",
    )
    col2.metric(
        "Scope 1 — Fleet",
        f"{scope1:,.0f} tCO₂e",
        f"{scope1 / total * 100:.0f}% of portfolio",
        delta_color="off",
    )
    col3.metric(
        "Scope 2 — Electricity",
        f"{scope2:,.0f} tCO₂e",
        f"{scope2 / total * 100:.0f}% of portfolio",
        delta_color="off",
    )
    col4.metric(
        "Scope 3 — Value Chain",
        f"{scope3:,.0f} tCO₂e",
        f"{scope3 / total * 100:.0f}% of portfolio — dominant",
        delta_color="inverse",
    )

    chart_col1, chart_col2 = st.columns(2)
    with chart_col1:
        st.plotly_chart(scope_breakdown_chart(emissions_df), use_container_width=True)
    with chart_col2:
        st.plotly_chart(monthly_trend_chart(emissions_df), use_container_width=True)

    st.plotly_chart(net_zero_pathway_chart(emissions_df), use_container_width=True)

    st.divider()
    st.markdown("""
<p style="font-size:0.78rem; color:#5A6E82; margin:0 0 0.5rem 0;">
  Full Scope 1/2/3 inventory — 96 monthly records across fleet, electricity, travel &amp; supply chain
</p>
""", unsafe_allow_html=True)
    st.download_button(
        label="Download Emissions CSV",
        data=emissions_df.to_csv(index=False).encode("utf-8"),
        file_name="emissions_inventory.csv",
        mime="text/csv",
    )

# ── Smart Meter Tab ─────────────────────────────────────────────────────────

with tab_meter:
    st.markdown("""
<div style="margin:0.25rem 0 0.8rem 0; padding:0.4rem 0.75rem; border-left:3px solid #009FE3; background:#F8FBFF; border-radius:0 4px 4px 0;">
  <p style="margin:0; font-size:0.62rem; letter-spacing:2px; text-transform:uppercase; color:#6B8CAE; font-weight:600;">Smart Meter</p>
  <p style="margin:2px 0 0 0; font-size:1rem; font-weight:700; color:#003F87;">Energy Consumption</p>
</div>
""", unsafe_allow_html=True)

    meter_kpis = compute_meter_kpis(meter_df)

    meter_totals = meter_df.groupby("meter_id")["kwh"].sum()
    peak_id = meter_totals.idxmax()
    peak_loc = meter_df[meter_df["meter_id"] == peak_id]["location"].iloc[0]
    peak_pct = meter_totals[peak_id] / meter_kpis["total_kwh"] * 100

    m_col1, m_col2, m_col3 = st.columns(3)
    m_col1.metric("Total Consumption", f"{meter_kpis['total_kwh']:,.0f} kWh")
    m_col2.metric("Electricity Emissions", f"{meter_kpis['total_co2e']:.2f} tCO₂e")
    m_col3.metric("Peak Location", peak_loc, f"{peak_pct:.0f}% of total consumption", delta_color="off")

    st.markdown("""
<div style="padding:0.45rem 0.75rem; background:#F0F6FC; border-left:3px solid #009FE3; border-radius:0 4px 4px 0; margin:0.5rem 0 0.75rem 0; font-size:0.78rem; color:#5A6E82;">
  Conversion: kWh &times; 0.20493 kgCO₂e/kWh &divide; 1,000 = tCO₂e &nbsp;&middot;&nbsp; BEIS 2024 UK grid average emission factor
</div>
""", unsafe_allow_html=True)

    chart_col1, chart_col2 = st.columns(2)
    with chart_col1:
        st.plotly_chart(energy_stacked_chart(meter_df), use_container_width=True)
    with chart_col2:
        st.plotly_chart(energy_rolling_chart(meter_df), use_container_width=True)

    st.markdown("""
<div style="margin:1rem 0 0.5rem 0; padding:0.4rem 0.75rem; border-left:3px solid #009FE3; background:#F8FBFF; border-radius:0 4px 4px 0;">
  <p style="margin:0; font-size:0.62rem; letter-spacing:2px; text-transform:uppercase; color:#6B8CAE; font-weight:600;">Data</p>
  <p style="margin:2px 0 0 0; font-size:1rem; font-weight:700; color:#003F87;">Raw Daily Readings</p>
</div>
""", unsafe_allow_html=True)

    st.dataframe(
        meter_df[["date", "meter_id", "location", "kwh"]],
        column_config={
            "date": st.column_config.DateColumn("Date", format="DD MMM YYYY"),
            "meter_id": st.column_config.TextColumn("Meter ID"),
            "location": st.column_config.TextColumn("Location"),
            "kwh": st.column_config.NumberColumn("Consumption (kWh)", format="%.1f"),
        },
        use_container_width=True,
        hide_index=True,
    )
