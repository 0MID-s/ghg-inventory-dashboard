"""Data loading functions for GHG Inventory Dashboard.

NOTE: This module imports streamlit only for @st.cache_data decorator.
The decorator is a no-op when streamlit is not running (safe to import).
"""
import pandas as pd
import streamlit as st


@st.cache_data
def load_emissions() -> pd.DataFrame:
    """Load synthetic monthly emissions data from data/emissions.csv.

    Returns a DataFrame with columns:
        date (datetime64), scope (str), category (str), co2e_tonnes (float),
        source (str), emission_factor (float), ef_unit (str)

    Raises:
        ValueError: if expected columns are missing.
    """
    df = pd.read_csv("data/emissions.csv", parse_dates=["date"])
    required = {"date", "scope", "category", "co2e_tonnes", "source", "emission_factor", "ef_unit"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"emissions.csv missing columns: {missing}")
    # Enforce types
    df["co2e_tonnes"] = df["co2e_tonnes"].astype(float)
    df["scope"] = df["scope"].astype(str)
    return df


@st.cache_data
def load_smart_meter() -> pd.DataFrame:
    """Load synthetic daily smart meter readings from data/smart_meter.csv.

    Returns a DataFrame with columns:
        date (datetime64), meter_id (str), kwh (float), location (str)

    Raises:
        ValueError: if expected columns are missing.
    """
    df = pd.read_csv("data/smart_meter.csv", parse_dates=["date"])
    required = {"date", "meter_id", "kwh", "location"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"smart_meter.csv missing columns: {missing}")
    df["kwh"] = df["kwh"].astype(float)
    return df
