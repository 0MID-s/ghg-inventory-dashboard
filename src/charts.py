"""
Plotly figure factory functions for the GHG Inventory Dashboard.

Design rule: NO 'import streamlit' in this file.
All functions accept pandas DataFrames and return plotly go.Figure objects.
"""
import pandas as pd
import plotly.graph_objects as go

_SCOPE_COLOURS = {
    "Scope 1": "#003F87",
    "Scope 2": "#009FE3",
    "Scope 3": "#00A3AD",
}
_METER_COLOURS = {
    "METER-001": "#003F87",   # Office Floor 1 — navy
    "METER-002": "#009FE3",   # Office Floor 2 — sky blue
    "METER-003": "#E07B00",   # Server Room — amber (visually distinct)
}

_BASE = dict(
    plot_bgcolor="white",
    paper_bgcolor="white",
    margin=dict(t=45, b=40, l=10, r=10),
    font=dict(family="sans-serif", size=11, color="#1C2B4A"),
    hoverlabel=dict(bgcolor="white", bordercolor="#CCE4F5", font_size=12),
)
_AXES = dict(
    xaxis=dict(gridcolor="#EEF4FB", linecolor="#CCE4F5", tickfont=dict(size=10), showgrid=True),
    yaxis=dict(gridcolor="#EEF4FB", linecolor="#CCE4F5", tickfont=dict(size=10), showgrid=True),
)


def _rgba(hex_colour: str, alpha: float) -> str:
    r, g, b = int(hex_colour[1:3], 16), int(hex_colour[3:5], 16), int(hex_colour[5:7], 16)
    return f"rgba({r},{g},{b},{alpha})"


def scope_breakdown_chart(df: pd.DataFrame) -> go.Figure:
    """Donut chart showing Scope 1/2/3 proportional breakdown with total annotation."""
    scope_totals = df.groupby("scope")["co2e_tonnes"].sum().reset_index()
    total = scope_totals["co2e_tonnes"].sum()
    colours = [_SCOPE_COLOURS.get(s, "#999") for s in scope_totals["scope"]]

    fig = go.Figure(data=[go.Pie(
        labels=scope_totals["scope"],
        values=scope_totals["co2e_tonnes"],
        hole=0.58,
        marker=dict(colors=colours, line=dict(color="#FFFFFF", width=2)),
        textinfo="percent",
        textfont=dict(size=12, color="#FFFFFF"),
        direction="clockwise",
        sort=False,
        hovertemplate="<b>%{label}</b><br>%{value:,.1f} tCO₂e &nbsp;·&nbsp; %{percent}<extra></extra>",
    )])

    fig.add_annotation(
        text=f"<b>{total:,.0f}</b><br>tCO₂e",
        x=0.5, y=0.5, showarrow=False,
        font=dict(size=15, color="#003F87"),
        align="center",
    )

    fig.update_layout(
        title=dict(text="Scope Breakdown", font=dict(size=13, color="#1C2B4A"), x=0),
        legend=dict(orientation="v", x=0.78, y=0.5, font=dict(size=11)),
        **_BASE,
    )
    return fig


def monthly_trend_chart(df: pd.DataFrame) -> go.Figure:
    """Area-fill line chart of Scope 1/2/3 emissions over the latest 12 months."""
    df = df.copy()
    df["month"] = pd.to_datetime(df["date"]).dt.to_period("M").astype(str)
    df["year"] = pd.to_datetime(df["date"]).dt.year
    latest_year = df["year"].max()
    monthly = (
        df[df["year"] == latest_year]
        .groupby(["month", "scope"])["co2e_tonnes"]
        .sum()
        .reset_index()
    )

    fig = go.Figure()
    for scope in sorted(monthly["scope"].unique()):
        data = monthly[monthly["scope"] == scope].sort_values("month")
        colour = _SCOPE_COLOURS.get(scope, "#999")
        fig.add_trace(go.Scatter(
            x=data["month"],
            y=data["co2e_tonnes"],
            name=scope,
            mode="lines+markers",
            line=dict(color=colour, width=2),
            marker=dict(size=5, color=colour),
            fill="tozeroy",
            fillcolor=_rgba(colour, 0.07),
            hovertemplate=f"<b>{scope}</b><br>%{{x}}<br>%{{y:,.1f}} tCO₂e<extra></extra>",
        ))

    fig.update_layout(
        title=dict(text="Monthly Emissions — FY 2024", font=dict(size=13, color="#1C2B4A"), x=0),
        yaxis_title="tCO₂e",
        legend=dict(title=None, orientation="h", y=-0.22, font=dict(size=11)),
        **_BASE,
        **_AXES,
    )
    return fig


def net_zero_pathway_chart(df: pd.DataFrame) -> go.Figure:
    """Bar chart of actuals overlaid with a dashed –45% by 2030 target pathway."""
    df = df.copy()
    df["year"] = pd.to_datetime(df["date"]).dt.year
    actuals = df.groupby("year")["co2e_tonnes"].sum().reset_index()
    actuals.columns = ["year", "co2e"]

    base_year = int(actuals["year"].min())
    base_value = float(actuals.loc[actuals["year"] == base_year, "co2e"].iloc[0])
    target_year = 2030
    target_value = base_value * 0.55  # −45% reduction from base year

    pathway_years = list(range(base_year, target_year + 1))
    pathway_values = [
        base_value + (target_value - base_value) * (y - base_year) / (target_year - base_year)
        for y in pathway_years
    ]

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=actuals["year"],
        y=actuals["co2e"],
        name="Actual",
        marker_color="#003F87",
        width=0.4,
        hovertemplate="<b>%{x}</b><br>%{y:,.1f} tCO₂e (actual)<extra></extra>",
    ))

    fig.add_trace(go.Scatter(
        x=pathway_years,
        y=pathway_values,
        name="−45% target pathway (2030)",
        mode="lines+markers",
        line=dict(color="#E07B00", width=2, dash="dash"),
        marker=dict(size=5, color="#E07B00"),
        hovertemplate="<b>Target %{x}</b><br>%{y:,.1f} tCO₂e<extra></extra>",
    ))

    fig.add_annotation(
        x=target_year, y=target_value,
        text=f"<b>{target_value:,.0f} tCO₂e</b><br>2030 target (−45%)",
        showarrow=True, arrowhead=2, arrowcolor="#E07B00",
        ax=40, ay=-35,
        font=dict(size=10, color="#E07B00"),
        bgcolor="white", bordercolor="#E07B00", borderwidth=1,
    )

    fig.update_layout(
        title=dict(text="Emissions vs. 2030 Reduction Target", font=dict(size=13, color="#1C2B4A"), x=0),
        yaxis_title="tCO₂e",
        xaxis=dict(
            tickvals=pathway_years,
            ticktext=[str(y) for y in pathway_years],
            gridcolor="#EEF4FB", linecolor="#CCE4F5", tickfont=dict(size=10), showgrid=True,
        ),
        yaxis=dict(gridcolor="#EEF4FB", linecolor="#CCE4F5", tickfont=dict(size=10), rangemode="tozero", showgrid=True),
        legend=dict(title=None, orientation="h", y=-0.22, font=dict(size=11)),
        **_BASE,
    )
    return fig


def energy_stacked_chart(df: pd.DataFrame) -> go.Figure:
    """Stacked area chart of daily kWh by meter location — shows total and breakdown simultaneously."""
    location_map = df.drop_duplicates("meter_id").set_index("meter_id")["location"].to_dict()

    fig = go.Figure()
    for meter_id in sorted(df["meter_id"].unique()):
        data = df[df["meter_id"] == meter_id].sort_values("date")
        colour = _METER_COLOURS.get(meter_id, "#999")
        label = location_map.get(meter_id, meter_id)
        fig.add_trace(go.Scatter(
            x=data["date"],
            y=data["kwh"],
            name=label,
            mode="lines",
            line=dict(color=colour, width=1.5),
            fillcolor=_rgba(colour, 0.60),
            stackgroup="one",
            hovertemplate=f"<b>{label}</b><br>%{{x|%d %b %Y}}<br>%{{y:,.1f}} kWh<extra></extra>",
        ))

    fig.update_layout(
        title=dict(text="Daily Consumption by Location", font=dict(size=13, color="#1C2B4A"), x=0),
        yaxis_title="kWh",
        legend=dict(title=None, orientation="h", y=-0.18, font=dict(size=11)),
        **_BASE,
        **_AXES,
    )
    return fig


def energy_rolling_chart(df: pd.DataFrame) -> go.Figure:
    """7-day rolling average kWh per meter with area fills."""
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values(["meter_id", "date"])
    df["kwh_7d"] = df.groupby("meter_id")["kwh"].transform(
        lambda x: x.rolling(7, min_periods=1).mean()
    )
    location_map = df.drop_duplicates("meter_id").set_index("meter_id")["location"].to_dict()

    fig = go.Figure()
    for meter_id in sorted(df["meter_id"].unique()):
        data = df[df["meter_id"] == meter_id]
        colour = _METER_COLOURS.get(meter_id, "#999")
        label = location_map.get(meter_id, meter_id)
        fig.add_trace(go.Scatter(
            x=data["date"],
            y=data["kwh_7d"],
            name=label,
            mode="lines",
            line=dict(color=colour, width=2),
            fill="tozeroy",
            fillcolor=_rgba(colour, 0.09),
            hovertemplate=f"<b>{label}</b><br>%{{x|%d %b %Y}}<br>%{{y:,.1f}} kWh (7d avg)<extra></extra>",
        ))

    fig.update_layout(
        title=dict(text="7-Day Rolling Average — Smoothed Trend", font=dict(size=13, color="#1C2B4A"), x=0),
        yaxis_title="kWh",
        legend=dict(title=None, orientation="h", y=-0.18, font=dict(size=11)),
        **_BASE,
        **_AXES,
    )
    return fig
