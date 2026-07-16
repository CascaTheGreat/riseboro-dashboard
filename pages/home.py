"""
pages/home.py
-------------
Riseboro Predictive Analytics Dashboard
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import pandas as pd

from streamlit_echarts import st_echarts
from src.components import metric_card, section_header, divider

# ── Primary colour & palette ─────────────────────────────────────────────────
PRIMARY   = "#013494"
PRIMARY_L = "#0252cc"
ACCENT    = "#1e88e5"
COLORS    = [PRIMARY, PRIMARY_L, ACCENT, "#42a5f5", "#90caf9", "#bbdefb"]

# ─────────────────────────────────────────────────────────────────────────────
# PAGE-LEVEL STYLE INJECTION
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
        /* Google Font */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

        html, body, [class*="css"]  { font-family: 'Inter', sans-serif; }

        /* Hero banner */
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

        /* Chart card wrapper */
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

        /* Upload zone */
        .upload-zone {
            border: 2px dashed #013494;
            border-radius: 16px;
            padding: 2rem;
            text-align: center;
            background: #f0f7ff;
            color: #013494;
            font-weight: 600;
            margin-bottom: 1rem;
        }

        /* Sidebar accent */
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #013494 0%, #0a2d6e 100%);
            color: white;
        }
        section[data-testid="stSidebar"] * { color: white !important; }
        section[data-testid="stSidebar"] .stSelectbox label { color: white !important; }
        section[data-testid="stSidebar"] hr { border-color: rgba(255,255,255,0.2); }
    </style>
    """,
    unsafe_allow_html=True,
)


# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Dashboard Controls")
    st.markdown("---")

    # Date range filter (decorative for mock data)
    st.markdown("**📅 Date Range**")
    date_options = ["Last 7 Days", "Last 30 Days", "Last Quarter", "YTD"]
    selected_range = st.selectbox("", date_options, label_visibility="collapsed")

    st.markdown("---")
    st.markdown("**📂 Active Dataset**")
    st.info("Mock data loaded. Upload CSV below to override.", icon="ℹ️")

    st.markdown("---")
    st.markdown("**🎨 Chart Theme**")
    chart_theme = st.radio("", ["Default", "Vintage", "Dark"], label_visibility="collapsed")

    st.markdown("---")
    st.caption("Riseboro Predictive Analytics v1.0")


# ─────────────────────────────────────────────────────────────────────────────
# HERO BANNER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(
    f"""
    <div class="hero-banner">
        <h1>📊 Riseboro Analytics Dashboard</h1>
        <p>Predictive insights &amp; program performance — {selected_range}</p>
    </div>
    """,
    unsafe_allow_html=True,
)


# ─────────────────────────────────────────────────────────────────────────────
# KPI METRIC CARDS
# ─────────────────────────────────────────────────────────────────────────────
section_header("Key Performance Indicators", "Summary metrics for the selected period")
divider()

k1, k2, k3, k4 = st.columns(4)
with k1:
    metric_card("Total Participants",  "2,847", "12.4%", True,  "👥")
with k2:
    metric_card("Program Completion",  "78.3%", "3.1%",  True,  "✅")
with k3:
    metric_card("Avg. Outcome Score",  "84.2",  "1.7%",  False, "📈")
with k4:
    metric_card("Active Enrollments",  "1,203", "8.9%",  True,  "🎓")

st.markdown("<br>", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# ROW 1: Monthly Trend (Line) + Program Mix (Pie Donut)
# ─────────────────────────────────────────────────────────────────────────────
section_header("Program Trends & Distribution")
divider()

col_l, col_r = st.columns([3, 2])

# ── Monthly Enrollment Trend ──────────────────────────────────────────────────
with col_l:
    st.markdown('<div class="chart-card"><div class="chart-card-title">📅 Monthly Enrollment Trend</div>', unsafe_allow_html=True)
    trend_options = {
        "color": COLORS,
        "tooltip": {"trigger": "axis"},
        "legend": {"data": ["New Enrollments", "Completions"], "bottom": 0},
        "grid": {"left": "3%", "right": "4%", "bottom": "12%", "containLabel": True},
        "xAxis": {
            "type": "category",
            "data": ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                     "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
        },
        "yAxis": {"type": "value"},
        "series": [
            {
                "name": "New Enrollments",
                "type": "line",
                "smooth": True,
                "lineStyle": {"width": 3, "color": PRIMARY},
                "areaStyle": {"opacity": 0.15, "color": PRIMARY},
                "data": [210, 235, 278, 312, 289, 334, 365, 398, 421, 389, 402, 445],
            },
            {
                "name": "Completions",
                "type": "line",
                "smooth": True,
                "lineStyle": {"width": 3, "color": ACCENT},
                "areaStyle": {"opacity": 0.1, "color": ACCENT},
                "data": [155, 182, 204, 241, 220, 265, 289, 311, 334, 305, 318, 354],
            },
        ],
    }
    st_echarts(options=trend_options, height="350px", key="line_trend")
    st.markdown('</div>', unsafe_allow_html=True)

# ── Program Mix Donut ─────────────────────────────────────────────────────────
with col_r:
    st.markdown('<div class="chart-card"><div class="chart-card-title">🥧 Program Distribution</div>', unsafe_allow_html=True)
    donut_options = {
        "color": COLORS,
        "tooltip": {"trigger": "item", "formatter": "{b}: {c} ({d}%)"},
        "legend": {"orient": "vertical", "left": "left", "top": "middle"},
        "series": [
            {
                "name": "Programs",
                "type": "pie",
                "radius": ["42%", "70%"],
                "avoidLabelOverlap": False,
                "itemStyle": {"borderRadius": 8, "borderColor": "#fff", "borderWidth": 2},
                "label": {"show": False, "position": "center"},
                "emphasis": {
                    "label": {"show": True, "fontSize": 18, "fontWeight": "bold"}
                },
                "labelLine": {"show": False},
                "data": [
                    {"value": 892, "name": "Housing"},
                    {"value": 654, "name": "Workforce"},
                    {"value": 521, "name": "Youth Dev."},
                    {"value": 438, "name": "Health"},
                    {"value": 342, "name": "Education"},
                ],
            }
        ],
    }
    st_echarts(options=donut_options, height="350px", key="donut_programs")
    st.markdown('</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# ROW 2: Outcome Scores (Bar) + Retention Gauge
# ─────────────────────────────────────────────────────────────────────────────
section_header("Outcomes & Retention")
divider()

col_b, col_g = st.columns([3, 2])

# ── Outcome Scores by Program ─────────────────────────────────────────────────
with col_b:
    st.markdown('<div class="chart-card"><div class="chart-card-title">📊 Avg. Outcome Scores by Program</div>', unsafe_allow_html=True)
    bar_options = {
        "color": COLORS,
        "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
        "legend": {"data": ["Q1", "Q2", "Q3", "Q4"], "bottom": 0},
        "grid": {"left": "3%", "right": "4%", "bottom": "12%", "containLabel": True},
        "xAxis": {
            "type": "category",
            "data": ["Housing", "Workforce", "Youth Dev.", "Health", "Education"],
        },
        "yAxis": {"type": "value", "max": 100},
        "series": [
            {"name": "Q1", "type": "bar", "barGap": "5%",
             "data": [72, 68, 81, 74, 79], "itemStyle": {"borderRadius": [4, 4, 0, 0]}},
            {"name": "Q2", "type": "bar",
             "data": [78, 74, 83, 77, 82], "itemStyle": {"borderRadius": [4, 4, 0, 0]}},
            {"name": "Q3", "type": "bar",
             "data": [81, 79, 86, 80, 84], "itemStyle": {"borderRadius": [4, 4, 0, 0]}},
            {"name": "Q4", "type": "bar",
             "data": [85, 83, 89, 84, 87], "itemStyle": {"borderRadius": [4, 4, 0, 0]}},
        ],
    }
    st_echarts(options=bar_options, height="350px", key="bar_outcomes")
    st.markdown('</div>', unsafe_allow_html=True)

# ── Retention Gauge ───────────────────────────────────────────────────────────
with col_g:
    st.markdown('<div class="chart-card"><div class="chart-card-title">🎯 Program Retention Rate</div>', unsafe_allow_html=True)
    gauge_options = {
        "series": [
            {
                "type": "gauge",
                "startAngle": 200,
                "endAngle": -20,
                "min": 0,
                "max": 100,
                "splitNumber": 5,
                "itemStyle": {"color": PRIMARY},
                "progress": {"show": True, "width": 20},
                "pointer": {"show": False},
                "axisLine": {"lineStyle": {"width": 20, "color": [[1, "#e2e8f0"]]}},
                "axisTick": {"show": False},
                "splitLine": {"show": False},
                "axisLabel": {"show": False},
                "anchor": {"show": False},
                "title": {"show": True, "offsetCenter": [0, "20%"],
                          "fontSize": 14, "color": "#64748b"},
                "detail": {
                    "valueAnimation": True,
                    "offsetCenter": [0, "-10%"],
                    "fontSize": 52,
                    "fontWeight": "bold",
                    "formatter": "{value}%",
                    "color": PRIMARY,
                },
                "data": [{"value": 78, "name": "Retention"}],
            }
        ]
    }
    st_echarts(options=gauge_options, height="350px", key="gauge_retention")
    st.markdown('</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# ROW 3: Geographic / Stacked Bar Breakdown
# ─────────────────────────────────────────────────────────────────────────────
section_header("Borough Breakdown", "Participant distribution across NYC boroughs")
divider()

st.markdown('<div class="chart-card"><div class="chart-card-title">🗺️ Participants by Borough & Program Type</div>', unsafe_allow_html=True)
stacked_options = {
    "color": COLORS,
    "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
    "legend": {
        "data": ["Housing", "Workforce", "Youth Dev.", "Health", "Education"],
        "bottom": 0,
    },
    "grid": {"left": "3%", "right": "4%", "bottom": "10%", "containLabel": True},
    "xAxis": {
        "type": "category",
        "data": ["Bronx", "Brooklyn", "Manhattan", "Queens", "Staten Island"],
    },
    "yAxis": {"type": "value"},
    "series": [
        {
            "name": "Housing", "type": "bar", "stack": "total",
            "data": [312, 278, 198, 234, 87],
            "itemStyle": {"borderRadius": [0, 0, 0, 0]},
        },
        {
            "name": "Workforce", "type": "bar", "stack": "total",
            "data": [201, 189, 156, 178, 62],
        },
        {
            "name": "Youth Dev.", "type": "bar", "stack": "total",
            "data": [178, 162, 134, 145, 55],
        },
        {
            "name": "Health", "type": "bar", "stack": "total",
            "data": [145, 138, 112, 128, 48],
        },
        {
            "name": "Education", "type": "bar", "stack": "total",
            "data": [112, 104, 89, 98, 39],
            "itemStyle": {"borderRadius": [4, 4, 0, 0]},
        },
    ],
}
st_echarts(options=stacked_options, height="380px", key="stacked_borough")
st.markdown('</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# CSV UPLOAD SECTION
# ─────────────────────────────────────────────────────────────────────────────
section_header("📂 Upload Your Data", "Upload a CSV to explore your own dataset")
divider()

st.markdown(
    """
    <div class="upload-zone">
        ⬆️ &nbsp; Drag &amp; drop a CSV file here, or click Browse to select
    </div>
    """,
    unsafe_allow_html=True,
)

uploaded_file = st.file_uploader(
    "Choose a CSV file",
    type=["csv"],
    label_visibility="collapsed",
    key="csv_uploader",
)

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        st.success(f"✅ Loaded **{uploaded_file.name}** — {len(df):,} rows × {len(df.columns)} columns")

        # ── Preview ───────────────────────────────────────────────────────────
        with st.expander("🔍 Data Preview (first 50 rows)", expanded=True):
            st.dataframe(df.head(50), use_container_width=True)

        # ── Auto-summary ──────────────────────────────────────────────────────
        num_cols = df.select_dtypes(include="number").columns.tolist()
        cat_cols = df.select_dtypes(include="object").columns.tolist()

        with st.expander("📈 Auto-generated Charts", expanded=True):
            if num_cols:
                col_pick_x = st.selectbox("X-axis (category / date)", cat_cols or df.columns.tolist(), key="csv_x")
                col_pick_y = st.selectbox("Y-axis (numeric)", num_cols, key="csv_y")

                agg = df.groupby(col_pick_x)[col_pick_y].mean().reset_index()
                agg.columns = ["label", "value"]
                agg = agg.head(20)  # cap for readability

                csv_chart_options = {
                    "color": [PRIMARY],
                    "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
                    "grid": {"left": "3%", "right": "4%", "bottom": "15%", "containLabel": True},
                    "xAxis": {
                        "type": "category",
                        "data": agg["label"].astype(str).tolist(),
                        "axisLabel": {"rotate": 30},
                    },
                    "yAxis": {"type": "value", "name": col_pick_y},
                    "series": [
                        {
                            "name": col_pick_y,
                            "type": "bar",
                            "data": agg["value"].round(2).tolist(),
                            "itemStyle": {"borderRadius": [6, 6, 0, 0], "color": PRIMARY},
                        }
                    ],
                }
                st_echarts(options=csv_chart_options, height="400px", key="csv_bar")
            else:
                st.info("No numeric columns found for charting. Try a different file.", icon="ℹ️")

        # ── Descriptive stats ─────────────────────────────────────────────────
        with st.expander("🧮 Descriptive Statistics"):
            if num_cols:
                st.dataframe(df[num_cols].describe().T.round(2), use_container_width=True)
            else:
                st.info("No numeric columns to describe.")

    except Exception as e:
        st.error(f"❌ Error reading file: {e}")

else:
    # Show a sample schema hint
    st.caption("💡 **Tip:** Try uploading a CSV with columns like `program`, `borough`, `participants`, `completion_rate`, etc.")


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
