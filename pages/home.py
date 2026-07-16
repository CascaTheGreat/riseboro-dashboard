"""
pages/home.py
-------------
Riseboro Work-Order Analytics Dashboard
Driven by data uploaded via pages/upload.py (session_state.wo_df).
Columns: WO, Prop-Unit, Building, Status, Call Date, Start Date,
         Employee, Brief Desc, Quantity, Stock, Stock Description,
         Unit Price, Total
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import pandas as pd

from streamlit_echarts import st_echarts
from src.components import metric_card, section_header, divider

# ── Palette ──────────────────────────────────────────────────────────────────
PRIMARY   = "#013494"
PRIMARY_L = "#0252cc"
ACCENT    = "#1e88e5"
COLORS    = [PRIMARY, PRIMARY_L, ACCENT, "#42a5f5", "#90caf9", "#bbdefb",
             "#e53935", "#fb8c00", "#43a047", "#8e24aa"]

# ─────────────────────────────────────────────────────────────────────────────
# PAGE STYLE
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
        html, body, [class*="css"]  { font-family: 'Inter', sans-serif; }

        .hero-banner {
            background: linear-gradient(120deg, #013494 0%, #0252cc 60%, #1565c0 100%);
            border-radius: 20px;
            padding: 2rem 2.5rem;
            color: white;
            margin-bottom: 1.5rem;
            box-shadow: 0 8px 32px rgba(1,52,148,0.3);
        }
        .hero-banner h1 { margin:0; font-size:1.9rem; font-weight:800; }
        .hero-banner p  { margin:0.4rem 0 0; opacity:.75; font-size:0.95rem; }

        .chart-card {
            background: white;
            border-radius: 16px;
            padding: 1.4rem;
            box-shadow: 0 2px 12px rgba(0,0,0,0.07);
            margin-bottom: 1rem;
        }
        .chart-card-title {
            color: #013494;
            font-weight: 700;
            font-size: 1rem;
            margin-bottom: 0.75rem;
        }

        /* empty state */
        .empty-state {
            background: linear-gradient(135deg, #f0f7ff 0%, #e8f0fe 100%);
            border: 2px dashed #013494;
            border-radius: 20px;
            padding: 3rem 2rem;
            text-align: center;
            color: #013494;
        }
        .empty-state h2 { font-size: 1.4rem; font-weight: 700; margin: 0.5rem 0; }
        .empty-state p  { opacity: 0.7; font-size: 0.95rem; }

        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #013494 0%, #0a2d6e 100%);
            color: white;
        }
        section[data-testid="stSidebar"] * { color: white !important; }
        section[data-testid="stSidebar"] hr { border-color: rgba(255,255,255,0.2); }
    </style>
    """,
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────────────────────────────────────
# LOAD DATA FROM SESSION STATE
# ─────────────────────────────────────────────────────────────────────────────
raw_df: pd.DataFrame | None = st.session_state.get("wo_df", None)
has_data = raw_df is not None and len(raw_df) > 0

# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Dashboard Controls")
    st.markdown("---")

    if has_data:
        # Date range filter on Call Date
        st.markdown("**📅 Filter by Call Date**")
        if "Call Date" in raw_df.columns and raw_df["Call Date"].notna().any():
            min_date = raw_df["Call Date"].min().date()
            max_date = raw_df["Call Date"].max().date()
            date_range = st.date_input(
                "Call date range",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date,
                label_visibility="collapsed",
                key="date_range",
            )
        else:
            date_range = None
            st.caption("No date data available.")

        st.markdown("---")

        # Building filter
        st.markdown("**🏢 Filter by Building**")
        buildings = sorted(raw_df["Building"].dropna().unique().tolist()) if "Building" in raw_df.columns else []
        selected_buildings = st.multiselect(
            "Select buildings",
            options=buildings,
            default=buildings,
            label_visibility="collapsed",
            key="bldg_filter",
        )

        st.markdown("---")

        # Status filter
        st.markdown("**🔵 Filter by Status**")
        statuses = sorted(raw_df["Status"].dropna().unique().tolist()) if "Status" in raw_df.columns else []
        selected_statuses = st.multiselect(
            "Select statuses",
            options=statuses,
            default=statuses,
            label_visibility="collapsed",
            key="status_filter",
        )

        st.markdown("---")
        st.success(f"✅ {len(raw_df):,} work orders loaded")
        filename = st.session_state.get("wo_filename", "")
        if filename:
            st.caption(f"Source: `{filename}`")

    else:
        st.info("No data loaded. Go to **Upload Work Orders** to import your CSV.", icon="ℹ️")
        date_range       = None
        selected_buildings = []
        selected_statuses  = []

    st.markdown("---")
    st.caption("Riseboro Predictive Analytics v1.0")


# ─────────────────────────────────────────────────────────────────────────────
# HERO BANNER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="hero-banner">
        <h1>📊 Riseboro Work-Order Dashboard</h1>
        <p>Maintenance analytics — spend, status, and building performance at a glance.</p>
    </div>
    """,
    unsafe_allow_html=True,
)


# ─────────────────────────────────────────────────────────────────────────────
# EMPTY STATE GATE
# ─────────────────────────────────────────────────────────────────────────────
if not has_data:
    st.markdown(
        """
        <div class="empty-state">
            <div style="font-size:3rem;">📂</div>
            <h2>No work-order data loaded</h2>
            <p>Head to <strong>Upload Work Orders</strong> in the sidebar to import your CSV,<br>
            then return here to see your analytics.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.stop()


# ─────────────────────────────────────────────────────────────────────────────
# APPLY FILTERS
# ─────────────────────────────────────────────────────────────────────────────
df = raw_df.copy()

# Date range
if date_range and isinstance(date_range, (list, tuple)) and len(date_range) == 2:
    start_dt, end_dt = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])
    if "Call Date" in df.columns:
        df = df[df["Call Date"].between(start_dt, end_dt, inclusive="both")]

# Building
if selected_buildings and "Building" in df.columns:
    df = df[df["Building"].isin(selected_buildings)]

# Status
if selected_statuses and "Status" in df.columns:
    df = df[df["Status"].isin(selected_statuses)]


# ─────────────────────────────────────────────────────────────────────────────
# KPI CARDS
# ─────────────────────────────────────────────────────────────────────────────
section_header("Key Performance Indicators", f"Showing {len(df):,} work orders after filters")
divider()

total_wo    = len(df)
total_spend = df["Total"].sum()        if "Total"    in df.columns else 0
avg_unit    = df["Unit Price"].mean()  if "Unit Price" in df.columns else 0
open_count  = (df["Status"].str.lower().str.contains("open", na=False).sum()
               if "Status" in df.columns else 0)

k1, k2, k3, k4 = st.columns(4)
with k1:
    metric_card("Total Work Orders", f"{total_wo:,}",         "",                True,  "📋")
with k2:
    metric_card("Total Spend",       f"${total_spend:,.2f}",  "",                True,  "💰")
with k3:
    metric_card("Avg Unit Price",    f"${avg_unit:,.2f}",     "",                True,  "🏷️")
with k4:
    metric_card("Open Orders",       f"{open_count:,}",       "",                False, "🔓")

st.markdown("<br>", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# ROW 1 — WO Volume over Time + Status Distribution
# ─────────────────────────────────────────────────────────────────────────────
section_header("Volume & Status")
divider()

col_l, col_r = st.columns([3, 2])

# ── Work Orders by Month ──────────────────────────────────────────────────────
with col_l:
    st.markdown('<div class="chart-card"><div class="chart-card-title">📅 Work Orders by Month (Call Date)</div>', unsafe_allow_html=True)

    if "Call Date" in df.columns and df["Call Date"].notna().any():
        monthly = (
            df.assign(month=df["Call Date"].dt.to_period("M"))
            .groupby("month")
            .size()
            .reset_index(name="count")
            .sort_values("month")
        )
        monthly["month"] = monthly["month"].astype(str)

        vol_opts = {
            "color": [PRIMARY],
            "tooltip": {"trigger": "axis"},
            "grid": {"left": "3%", "right": "4%", "bottom": "10%", "containLabel": True},
            "xAxis": {"type": "category", "data": monthly["month"].tolist(),
                      "axisLabel": {"rotate": 30}},
            "yAxis": {"type": "value", "name": "Work Orders"},
            "series": [{
                "name": "WOs",
                "type": "bar",
                "data": monthly["count"].tolist(),
                "itemStyle": {"borderRadius": [4, 4, 0, 0], "color": PRIMARY},
                "emphasis": {"itemStyle": {"color": PRIMARY_L}},
            }],
        }
        st_echarts(options=vol_opts, height="350px", key="monthly_vol")
    else:
        st.info("No Call Date data available for timeline chart.")

    st.markdown("</div>", unsafe_allow_html=True)

# ── Status Donut ──────────────────────────────────────────────────────────────
with col_r:
    st.markdown('<div class="chart-card"><div class="chart-card-title">🔵 Status Distribution</div>', unsafe_allow_html=True)

    if "Status" in df.columns:
        status_counts = df["Status"].value_counts().reset_index()
        status_counts.columns = ["name", "value"]
        pie_data = status_counts.to_dict("records")

        status_opts = {
            "color": COLORS,
            "tooltip": {"trigger": "item", "formatter": "{b}: {c} ({d}%)"},
            "legend": {"orient": "vertical", "left": "left", "top": "middle"},
            "series": [{
                "name": "Status",
                "type": "pie",
                "radius": ["42%", "70%"],
                "avoidLabelOverlap": False,
                "itemStyle": {"borderRadius": 8, "borderColor": "#fff", "borderWidth": 2},
                "label": {"show": False, "position": "center"},
                "emphasis": {"label": {"show": True, "fontSize": 18, "fontWeight": "bold"}},
                "labelLine": {"show": False},
                "data": pie_data,
            }],
        }
        st_echarts(options=status_opts, height="350px", key="status_donut")
    else:
        st.info("No Status column available.")

    st.markdown("</div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# ROW 2 — Spend by Building + Top Employees
# ─────────────────────────────────────────────────────────────────────────────
section_header("Spend & Workforce")
divider()

col_b, col_e = st.columns([3, 2])

# ── Spend by Building ─────────────────────────────────────────────────────────
with col_b:
    st.markdown('<div class="chart-card"><div class="chart-card-title">🏢 Total Spend by Building (Top 12)</div>', unsafe_allow_html=True)

    if "Building" in df.columns and "Total" in df.columns:
        bldg_spend = (
            df.groupby("Building")["Total"].sum()
            .sort_values(ascending=False)
            .head(12)
            .reset_index()
        )
        spend_opts = {
            "color": [PRIMARY],
            "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"},
                        "formatter": "{b}<br/>Spend: ${c:,.2f}"},
            "grid": {"left": "3%", "right": "4%", "bottom": "18%", "containLabel": True},
            "xAxis": {
                "type": "category",
                "data": bldg_spend["Building"].tolist(),
                "axisLabel": {"rotate": 35, "fontSize": 11},
            },
            "yAxis": {"type": "value", "name": "Spend ($)"},
            "series": [{
                "name": "Spend",
                "type": "bar",
                "data": bldg_spend["Total"].round(2).tolist(),
                "itemStyle": {"borderRadius": [4, 4, 0, 0], "color": PRIMARY},
                "emphasis": {"itemStyle": {"color": PRIMARY_L}},
            }],
        }
        st_echarts(options=spend_opts, height="350px", key="bldg_spend")
    else:
        st.info("No Building / Total data available.")

    st.markdown("</div>", unsafe_allow_html=True)

# ── Top Employees by WO Count ─────────────────────────────────────────────────
with col_e:
    st.markdown('<div class="chart-card"><div class="chart-card-title">👷 Top 10 Employees by WO Count</div>', unsafe_allow_html=True)

    if "Employee" in df.columns:
        emp_counts = (
            df["Employee"].value_counts()
            .head(10)
            .reset_index()
        )
        emp_counts.columns = ["Employee", "Count"]

        emp_opts = {
            "color": COLORS,
            "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
            "grid": {"left": "3%", "right": "4%", "bottom": "5%", "containLabel": True},
            "xAxis": {"type": "value", "name": "WOs"},
            "yAxis": {
                "type": "category",
                "data": emp_counts["Employee"].tolist()[::-1],
                "axisLabel": {"fontSize": 11},
            },
            "series": [{
                "name": "Work Orders",
                "type": "bar",
                "data": emp_counts["Count"].tolist()[::-1],
                "itemStyle": {"borderRadius": [0, 4, 4, 0], "color": ACCENT},
            }],
        }
        st_echarts(options=emp_opts, height="350px", key="emp_wo")
    else:
        st.info("No Employee data available.")

    st.markdown("</div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# ROW 3 — Spend by Status (stacked) + Stock / Material Cost
# ─────────────────────────────────────────────────────────────────────────────
section_header("Status × Building Breakdown")
divider()

if "Building" in df.columns and "Status" in df.columns and "Total" in df.columns:
    top_buildings = (
        df.groupby("Building")["Total"].sum()
        .sort_values(ascending=False)
        .head(10)
        .index.tolist()
    )
    all_statuses = df["Status"].dropna().unique().tolist()

    pivot = (
        df[df["Building"].isin(top_buildings)]
        .groupby(["Building", "Status"])["Total"]
        .sum()
        .unstack(fill_value=0)
        .loc[top_buildings]
    )

    stacked_series = []
    for i, status in enumerate(pivot.columns):
        is_last = i == len(pivot.columns) - 1
        stacked_series.append({
            "name": status,
            "type": "bar",
            "stack": "total",
            "data": pivot[status].round(2).tolist(),
            "itemStyle": {"borderRadius": [4, 4, 0, 0] if is_last else [0, 0, 0, 0]},
        })

    stacked_opts = {
        "color": COLORS,
        "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
        "legend": {"data": list(pivot.columns), "bottom": 0},
        "grid": {"left": "3%", "right": "4%", "bottom": "12%", "containLabel": True},
        "xAxis": {
            "type": "category",
            "data": top_buildings,
            "axisLabel": {"rotate": 25, "fontSize": 11},
        },
        "yAxis": {"type": "value", "name": "Spend ($)"},
        "series": stacked_series,
    }

    st.markdown('<div class="chart-card"><div class="chart-card-title">📊 Spend by Building stacked by Status (Top 10 Buildings)</div>', unsafe_allow_html=True)
    st_echarts(options=stacked_opts, height="380px", key="stacked_bldg_status")
    st.markdown("</div>", unsafe_allow_html=True)
else:
    st.info("Need Building, Status, and Total columns to render this chart.")


# ─────────────────────────────────────────────────────────────────────────────
# ROW 4 — Top Stock / Materials
# ─────────────────────────────────────────────────────────────────────────────
section_header("Top Materials Used")
divider()

if "Stock Description" in df.columns and "Quantity" in df.columns:
    mat_cols = st.columns([3, 2])

    with mat_cols[0]:
        st.markdown('<div class="chart-card"><div class="chart-card-title">📦 Top 10 Stock Items by Quantity Used</div>', unsafe_allow_html=True)
        top_stock = (
            df.groupby("Stock Description")["Quantity"].sum()
            .sort_values(ascending=False)
            .head(10)
            .reset_index()
        )
        stock_opts = {
            "color": [ACCENT],
            "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
            "grid": {"left": "3%", "right": "4%", "bottom": "5%", "containLabel": True},
            "xAxis": {"type": "value", "name": "Total Qty"},
            "yAxis": {
                "type": "category",
                "data": top_stock["Stock Description"].tolist()[::-1],
                "axisLabel": {"fontSize": 10, "width": 160, "overflow": "truncate"},
            },
            "series": [{
                "name": "Quantity",
                "type": "bar",
                "data": top_stock["Quantity"].round(1).tolist()[::-1],
                "itemStyle": {"borderRadius": [0, 4, 4, 0], "color": ACCENT},
            }],
        }
        st_echarts(options=stock_opts, height="350px", key="top_stock_qty")
        st.markdown("</div>", unsafe_allow_html=True)

    with mat_cols[1]:
        if "Total" in df.columns:
            st.markdown('<div class="chart-card"><div class="chart-card-title">💸 Top 10 Stock Items by Cost</div>', unsafe_allow_html=True)
            top_cost = (
                df.groupby("Stock Description")["Total"].sum()
                .sort_values(ascending=False)
                .head(10)
                .reset_index()
            )
            cost_opts = {
                "color": [PRIMARY_L],
                "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
                "grid": {"left": "3%", "right": "4%", "bottom": "5%", "containLabel": True},
                "xAxis": {"type": "value", "name": "Total Cost ($)"},
                "yAxis": {
                    "type": "category",
                    "data": top_cost["Stock Description"].tolist()[::-1],
                    "axisLabel": {"fontSize": 10, "width": 160, "overflow": "truncate"},
                },
                "series": [{
                    "name": "Cost",
                    "type": "bar",
                    "data": top_cost["Total"].round(2).tolist()[::-1],
                    "itemStyle": {"borderRadius": [0, 4, 4, 0], "color": PRIMARY_L},
                }],
            }
            st_echarts(options=cost_opts, height="350px", key="top_stock_cost")
            st.markdown("</div>", unsafe_allow_html=True)
else:
    st.info("Stock Description and Quantity columns needed for material analysis.")


# ─────────────────────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown(
    """
    <div style="text-align:center; color:#94a3b8; font-size:0.8rem; padding:1rem 0;">
        Riseboro Predictive Analytics Dashboard &nbsp;·&nbsp; Built with Streamlit &amp; Apache ECharts
        &nbsp;·&nbsp; <a href="https://hoyalytics.org" style="color:#013494;">Hoyalytics</a>
    </div>
    """,
    unsafe_allow_html=True,
)
