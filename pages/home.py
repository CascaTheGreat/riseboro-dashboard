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
from src.helpers import classify_issue, get_season

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
        section[data-testid="stSidebar"] * { color: white; }
        section[data-testid="stSidebar"] hr { border-color: rgba(255,255,255,0.2); }
        section[data-testid="stSidebar"] .schema-pill {color: #013494;}
        section[data-testid="stSidebar"] input {color: #013494;}
        section[data-testid="stSidebar"] code {color: #013494;}
    </style>
    """,
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────────────────────────────────────
# LOAD DATA FROM SESSION STATE
# ─────────────────────────────────────────────────────────────────────────────
raw_df: pd.DataFrame | None = st.session_state.get("wo_df", None)
has_data = raw_df is not None and len(raw_df) > 0

if has_data:
    raw_df = raw_df.copy()
    if "Brief Desc" in raw_df.columns and "issue_category" not in raw_df.columns:
        raw_df["issue_category"] = raw_df["Brief Desc"].apply(classify_issue)
    if "Call Date" in raw_df.columns and "season" not in raw_df.columns:
        raw_df["season"] = raw_df["Call Date"].apply(get_season)

# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ️ Dashboard Controls")
    st.markdown("---")

    if has_data:
        # Date range filter on Call Date
        st.markdown("** Filter by Call Date**")
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
        st.markdown("** Filter by Building**")
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
        st.markdown("** Filter by Status**")
        statuses = sorted(raw_df["Status"].dropna().unique().tolist()) if "Status" in raw_df.columns else []
        selected_statuses = st.multiselect(
            "Select statuses",
            options=statuses,
            default=statuses,
            label_visibility="collapsed",
            key="status_filter",
        )

        st.markdown("---")
        st.success(f" {len(raw_df):,} work orders loaded")
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
        <h1> RB Prevent Dashboard</h1>
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
            <div style="font-size:3rem;"></div>
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

# ── Critical Maintenance KPIs ────────────────────────────────────────────────
section_header("️ Critical Maintenance KPIs", "Tracked categories: Leaks, Elevators, Heat, Hot Water, Roof")
divider()

target_categories = ["Leaks", "Elevators", "Heat", "Hot Water", "Roof"]

# Calculate 3-year threshold relative to max Call Date in raw_df
if "Call Date" in raw_df.columns and raw_df["Call Date"].notna().any():
    max_call_date = raw_df["Call Date"].max()
    three_years_ago = max_call_date - pd.DateOffset(years=3)
else:
    max_call_date = pd.Timestamp.now()
    three_years_ago = max_call_date - pd.DateOffset(years=3)

# Filter raw_df for target categories and last 3 years
recent_raw = raw_df[
    raw_df["issue_category"].isin(target_categories) &
    (raw_df["Call Date"] >= three_years_ago)
]

# Calculate high-volume counts for each category
category_high_vol_bldgs = {}
for cat in target_categories:
    cat_recent = recent_raw[recent_raw["issue_category"] == cat]
    cat_bldg_counts = cat_recent.groupby("Building").size()
    category_high_vol_bldgs[cat] = len(cat_bldg_counts[cat_bldg_counts > 3])

# Filtered counts
filtered_counts = {}
for cat in target_categories:
    filtered_counts[cat] = (df["issue_category"] == cat).sum()

c1, c2, c3, c4, c5 = st.columns(5)
with c1:
    h_bldgs = category_high_vol_bldgs["Leaks"]
    metric_card(
        "Leaks",
        f"{filtered_counts['Leaks']:,}",
        f"{h_bldgs} high-vol bldgs" if h_bldgs > 0 else "0 high-vol bldgs",
        h_bldgs == 0,
        "",
        show_arrow=False
    )
with c2:
    h_bldgs = category_high_vol_bldgs["Elevators"]
    metric_card(
        "Elevators",
        f"{filtered_counts['Elevators']:,}",
        f"{h_bldgs} high-vol bldgs" if h_bldgs > 0 else "0 high-vol bldgs",
        h_bldgs == 0,
        "",
        show_arrow=False
    )
with c3:
    h_bldgs = category_high_vol_bldgs["Heat"]
    metric_card(
        "Heat",
        f"{filtered_counts['Heat']:,}",
        f"{h_bldgs} high-vol bldgs" if h_bldgs > 0 else "0 high-vol bldgs",
        h_bldgs == 0,
        "",
        show_arrow=False
    )
with c4:
    h_bldgs = category_high_vol_bldgs["Hot Water"]
    metric_card(
        "Hot Water",
        f"{filtered_counts['Hot Water']:,}",
        f"{h_bldgs} high-vol bldgs" if h_bldgs > 0 else "0 high-vol bldgs",
        h_bldgs == 0,
        "️",
        show_arrow=False
    )
with c5:
    h_bldgs = category_high_vol_bldgs["Roof"]
    metric_card(
        "Roof",
        f"{filtered_counts['Roof']:,}",
        f"{h_bldgs} high-vol bldgs" if h_bldgs > 0 else "0 high-vol bldgs",
        h_bldgs == 0,
        "",
        show_arrow=False
    )

st.markdown("<br>", unsafe_allow_html=True)

# ── High-Volume Tracking & Seasonal Trends ───────────────────────────────────
section_header(" High-Volume Tracking & Seasonal Trends", "Analysis of critical issues over time and across the portfolio")
divider()

col_l, col_r = st.columns([4, 5])

# Left column: Seasonal Breakdown
with col_l:
    st.markdown('<div class="chart-card"><div class="chart-card-title">️ Seasonal Breakdown of Issues (Filtered Data)</div>', unsafe_allow_html=True)
    seasonal_df = df[df["issue_category"].isin(target_categories)]
    if not seasonal_df.empty and "season" in seasonal_df.columns:
        seasonal_pivot = (
            seasonal_df.groupby(["season", "issue_category"])
            .size()
            .unstack(fill_value=0)
        )
        seasons_order = ["Winter", "Spring", "Summer", "Fall"]
        seasonal_pivot = seasonal_pivot.reindex(seasons_order, fill_value=0)
        for cat in target_categories:
            if cat not in seasonal_pivot.columns:
                seasonal_pivot[cat] = 0
        
        colors_mapping = {
            "Leaks": "#1e88e5",      # Light Blue
            "Elevators": "#8e24aa",  # Purple
            "Heat": "#e53935",       # Red
            "Hot Water": "#fb8c00",  # Orange
            "Roof": "#43a047",       # Green
        }
        
        seasonal_series = []
        for cat in target_categories:
            seasonal_series.append({
                "name": cat,
                "type": "bar",
                "stack": "total",
                "data": seasonal_pivot[cat].tolist(),
                "itemStyle": {"borderRadius": [4, 4, 0, 0]},
            })
            
        seasonal_opts = {
            "color": [colors_mapping[cat] for cat in target_categories],
            "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
            "legend": {"data": target_categories, "bottom": 0},
            "grid": {"left": "3%", "right": "4%", "bottom": "12%", "containLabel": True},
            "xAxis": {"type": "category", "data": seasons_order},
            "yAxis": {"type": "value", "name": "Reports"},
            "series": seasonal_series,
        }
        st_echarts(options=seasonal_opts, height="380px", key="seasonal_breakdown_chart")
    else:
        st.info("No seasonal data available. Verify Call Date contains valid dates.")
    st.markdown('</div>', unsafe_allow_html=True)

# Right column: High-Volume Portfolio Tracking
with col_r:
    st.markdown('<div class="chart-card"><div class="chart-card-title"> High-Volume Issue Tracking (Last 3 Years)</div>', unsafe_allow_html=True)
    
    # High volume building tracking (>3 reports in last 3 years)
    bldg_piv = (
        recent_raw.groupby(["Building", "issue_category"])
        .size()
        .unstack(fill_value=0)
    )
    for cat in target_categories:
        if cat not in bldg_piv.columns:
            bldg_piv[cat] = 0
    bldg_piv = bldg_piv[target_categories]
    bldg_piv["Total Target Reports"] = bldg_piv.sum(axis=1)
    high_vol_bldgs = bldg_piv[bldg_piv["Total Target Reports"] > 3].sort_values(
        "Total Target Reports", ascending=False
    ).reset_index()

    bldg_info = raw_df[[
        "Building", "bc_ADDRESS", "bc_Borough", "bc_PROJECT_NAME"
    ]].drop_duplicates(subset=["Building"])
    
    high_vol_bldgs = high_vol_bldgs.merge(bldg_info, on="Building", how="left")
    high_vol_bldgs["bc_ADDRESS"] = high_vol_bldgs["bc_ADDRESS"].fillna("Unknown Address")
    high_vol_bldgs["bc_Borough"] = high_vol_bldgs["bc_Borough"].fillna("Unknown Borough")
    high_vol_bldgs["bc_PROJECT_NAME"] = high_vol_bldgs["bc_PROJECT_NAME"].fillna("Unknown Project")

    # High volume unit tracking
    if "Prop-Unit" in raw_df.columns:
        unit_raw = recent_raw[recent_raw["Prop-Unit"] != "Building"]
        unit_piv = (
            unit_raw.groupby(["Building", "Prop-Unit", "issue_category"])
            .size()
            .unstack(fill_value=0)
        )
        for cat in target_categories:
            if cat not in unit_piv.columns:
                unit_piv[cat] = 0
        unit_piv = unit_piv[target_categories]
        unit_piv["Total Target Reports"] = unit_piv.sum(axis=1)
        high_vol_units = unit_piv[unit_piv["Total Target Reports"] > 3].sort_values(
            "Total Target Reports", ascending=False
        ).reset_index()
        high_vol_units = high_vol_units.merge(bldg_info, on="Building", how="left")
        high_vol_units["bc_ADDRESS"] = high_vol_units["bc_ADDRESS"].fillna("Unknown Address")
        high_vol_units["bc_Borough"] = high_vol_units["bc_Borough"].fillna("Unknown Borough")
        high_vol_units["bc_PROJECT_NAME"] = high_vol_units["bc_PROJECT_NAME"].fillna("Unknown Project")
    else:
        high_vol_units = pd.DataFrame()

    tab_bldg, tab_unit = st.tabs([" High-Vol Buildings", " High-Vol Units"])
    
    with tab_bldg:
        st.caption("Buildings with >3 target reports (Leaks, Elevators, Heat, Hot Water, Roof) in the last 3 years.")
        if not high_vol_bldgs.empty:
            bldgs_display = high_vol_bldgs[[
                "Building", "bc_PROJECT_NAME", "bc_ADDRESS", 
                "Leaks", "Elevators", "Heat", "Hot Water", "Roof", "Total Target Reports"
            ]].copy()
            bldgs_display.columns = [
                "Building Code", "Project Name", "Address", 
                "Leaks", "Elevators", "Heat", "Hot Water", "Roof", "Total"
            ]
            st.dataframe(
                bldgs_display,
                column_config={
                    "Building Code": st.column_config.TextColumn("Building", pinned=True),
                    "Project Name": st.column_config.TextColumn("Project"),
                    "Address": st.column_config.TextColumn("Address"),
                    "Leaks": st.column_config.NumberColumn("Leaks", format="%d"),
                    "Elevators": st.column_config.NumberColumn("Elevators", format="%d"),
                    "Heat": st.column_config.NumberColumn("Heat", format="%d"),
                    "Hot Water": st.column_config.NumberColumn("Hot Water", format="%d"),
                    "Roof": st.column_config.NumberColumn("Roof", format="%d"),
                    "Total": st.column_config.NumberColumn("Total", format="%d"),
                },
                hide_index=True,
                height=300
            )
        else:
            st.success("No buildings identified with more than 3 target reports in the last 3 years.")
            
    with tab_unit:
        st.caption("Individual units with >3 target reports in the last 3 years.")
        if not high_vol_units.empty:
            units_display = high_vol_units[[
                "Building", "Prop-Unit", "bc_PROJECT_NAME",
                "Leaks", "Elevators", "Heat", "Hot Water", "Roof", "Total Target Reports"
            ]].copy()
            units_display.columns = [
                "Building Code", "Unit", "Project Name",
                "Leaks", "Elevators", "Heat", "Hot Water", "Roof", "Total"
            ]
            st.dataframe(
                units_display,
                column_config={
                    "Building Code": st.column_config.TextColumn("Building", pinned=True),
                    "Unit": st.column_config.TextColumn("Unit", pinned=True),
                    "Project Name": st.column_config.TextColumn("Project"),
                    "Leaks": st.column_config.NumberColumn("Leaks", format="%d"),
                    "Elevators": st.column_config.NumberColumn("Elevators", format="%d"),
                    "Heat": st.column_config.NumberColumn("Heat", format="%d"),
                    "Hot Water": st.column_config.NumberColumn("Hot Water", format="%d"),
                    "Roof": st.column_config.NumberColumn("Roof", format="%d"),
                    "Total": st.column_config.NumberColumn("Total", format="%d"),
                },
                hide_index=True,
                height=300
            )
        else:
            st.success("No individual units identified with more than 3 target reports in the last 3 years.")
            
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# ROW 1 — WO Volume over Time + Status Distribution
# ─────────────────────────────────────────────────────────────────────────────
section_header("Volume & Status")
divider()

col_l, col_r = st.columns([3, 2])

# ── Work Orders by Month ──────────────────────────────────────────────────────
with col_l:
    st.markdown('<div class="chart-card"><div class="chart-card-title"> Work Orders by Month (Call Date)</div>', unsafe_allow_html=True)

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
    st.markdown('<div class="chart-card"><div class="chart-card-title"> Status Distribution</div>', unsafe_allow_html=True)

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
