"""
KPI aggregations and emission factor conversions.

Design rule: NO 'import streamlit' in this file.
All functions accept plain Python/pandas types and return plain Python types.
This keeps the module testable without a running Streamlit server.
"""
import pandas as pd

# ---------------------------------------------------------------------------
# Emission factors — BEIS 2024 UK Government GHG Conversion Factors
# Source: https://www.gov.uk/government/collections/government-conversion-factors-for-company-reporting
# ---------------------------------------------------------------------------

# UK electricity grid average (market-based, includes T&D losses): kgCO2e/kWh
SCOPE2_EF_KG_PER_KWH = 0.20493

# Road diesel (well-to-wheel): kgCO2e/litre
SCOPE1_FLEET_EF_KG_PER_LITRE = 2.68490


def kwh_to_co2e(kwh: float) -> float:
    """Convert kilowatt-hours of electricity to tonnes CO2e.

    Uses BEIS 2024 UK grid average emission factor (0.20493 kgCO2e/kWh).
    Returns tCO2e (not kgCO2e).
    """
    return (kwh * SCOPE2_EF_KG_PER_KWH) / 1000


def litres_to_co2e(litres: float) -> float:
    """Convert litres of diesel to tonnes CO2e.

    Uses BEIS 2024 road diesel emission factor (2.68490 kgCO2e/litre).
    Returns tCO2e (not kgCO2e).
    """
    return (litres * SCOPE1_FLEET_EF_KG_PER_LITRE) / 1000


def compute_scope_totals(df: pd.DataFrame) -> dict:
    """Return total tCO2e per scope as a dict.

    Args:
        df: emissions DataFrame from load_emissions()

    Returns:
        dict mapping scope name -> total tCO2e (e.g., {"Scope 1": 120.4, ...})
    """
    return df.groupby("scope")["co2e_tonnes"].sum().to_dict()


def compute_kpis(df: pd.DataFrame) -> dict:
    """Compute all KPI scalars needed by app.py st.metric() cards.

    Args:
        df: emissions DataFrame from load_emissions()

    Returns:
        dict with keys:
            total_co2e (float): sum of all co2e_tonnes across all scopes and months
            yoy_pct (float): YoY % change — negative means reduction
            largest_scope (str): scope name with highest total tCO2e
            scope2_co2e (float): total tCO2e from Scope 2
            scope_totals (dict): {scope: total_co2e} for all scopes
    """
    total_co2e = df["co2e_tonnes"].sum()
    scope_totals = df.groupby("scope")["co2e_tonnes"].sum()
    largest_scope = scope_totals.idxmax()

    # YoY calculation: compare 2024 vs 2023 totals using 'year' extracted from date
    if "year" not in df.columns:
        df = df.copy()
        df["year"] = pd.to_datetime(df["date"]).dt.year

    years = sorted(df["year"].unique())
    if len(years) >= 2:
        prior_total = df[df["year"] == years[-2]]["co2e_tonnes"].sum()
        current_total = df[df["year"] == years[-1]]["co2e_tonnes"].sum()
        yoy_pct = ((current_total - prior_total) / prior_total * 100) if prior_total > 0 else 0.0
    else:
        yoy_pct = 0.0  # single-year fallback

    return {
        "total_co2e": float(total_co2e),
        "yoy_pct": round(float(yoy_pct), 1),
        "largest_scope": str(largest_scope),
        "scope2_co2e": float(scope_totals.get("Scope 2", 0)),
        "scope_totals": scope_totals.to_dict(),
    }


def compute_meter_kpis(df: pd.DataFrame) -> dict:
    """Aggregate KPIs from smart meter data.

    Args:
        df: smart meter DataFrame from load_smart_meter()
            Columns: date, meter_id, location, kwh

    Returns:
        dict with keys:
            total_kwh (float): sum of all kwh readings across all meters
            total_co2e (float): total tCO2e from electricity (BEIS 2024 factor)
    """
    total_kwh = float(df["kwh"].sum())
    total_co2e = kwh_to_co2e(total_kwh)
    return {
        "total_kwh": total_kwh,
        "total_co2e": total_co2e,
    }
