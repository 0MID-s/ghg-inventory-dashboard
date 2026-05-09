"""CSS injection for GHG Inventory Dashboard — returns HTML string, no streamlit import."""


def get_css() -> str:
    return """
<style>
/* ── Layout density ──────────────────────────────────────────────────────── */
.block-container {
    padding-top: 0.5rem !important;
    padding-bottom: 2rem !important;
}
section[data-testid="stSidebar"] .block-container {
    padding-top: 1rem !important;
}

/* ── Metric cards ────────────────────────────────────────────────────────── */
[data-testid="metric-container"] {
    background-color: #F0F6FC;
    border: 1px solid #CCE4F5;
    border-left: 4px solid #009FE3;
    border-radius: 6px;
    padding: 0.85rem 1.1rem;
}

/* ── Chart cards ─────────────────────────────────────────────────────────── */
[data-testid="stPlotlyChart"] {
    background-color: #FAFCFF;
    border: 1px solid #E5EEF8;
    border-radius: 8px;
    box-shadow: 0 1px 4px rgba(0,63,135,0.07);
    overflow: hidden;
    padding: 0.25rem;
}

/* ── Dataframe ───────────────────────────────────────────────────────────── */
[data-testid="stDataFrame"] {
    border: 1px solid #E5EEF8;
    border-radius: 6px;
    overflow: hidden;
}

/* ── Tab strip ───────────────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    border-bottom: 2px solid #CCE4F5;
    gap: 0.25rem;
}
.stTabs [data-baseweb="tab"] {
    padding-left: 1.25rem;
    padding-right: 1.25rem;
    font-weight: 500;
}

/* ── Sidebar ─────────────────────────────────────────────────────────────── */
section[data-testid="stSidebar"] {
    background-color: #F5F9FE;
    border-right: 1px solid #CCE4F5;
}

/* ── Download button ─────────────────────────────────────────────────────── */
[data-testid="stDownloadButton"] > button {
    background-color: #003F87 !important;
    color: white !important;
    border: none !important;
    font-weight: 600;
    letter-spacing: 0.3px;
}
[data-testid="stDownloadButton"] > button:hover {
    background-color: #009FE3 !important;
}
</style>
"""
