"""
pages/upload.py
---------------
Work Order CSV Upload — Riseboro Predictive Analytics
Accepts columns: WO, Prop-Unit, Building, Status, Call Date, Start Date,
                 Employee, Brief Desc, Quantity, Stock, Stock Description,
                 Unit Price, Total
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import pandas as pd

from src.components import section_header, divider

# ── Required schema ───────────────────────────────────────────────────────────
REQUIRED_COLUMNS = [
    "WO", "Prop-Unit", "Building", "Status",
    "Call Date", "Start Date", "Employee", "Brief Desc",
    "Quantity", "Stock", "Stock Description", "Unit Price", "Total",
]

DATE_COLS    = ["Call Date", "Start Date"]
NUMERIC_COLS = ["Quantity", "Unit Price", "Total"]

PRIMARY   = "#013494"
PRIMARY_L = "#0252cc"
ACCENT    = "#1e88e5"


# ─────────────────────────────────────────────────────────────────────────────
# PAGE STYLE
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
        html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

        /* Hero */
        .upload-hero {
            background: linear-gradient(120deg, #013494 0%, #0252cc 60%, #1565c0 100%);
            border-radius: 20px;
            padding: 2rem 2.5rem;
            color: white;
            margin-bottom: 1.5rem;
            box-shadow: 0 8px 32px rgba(1,52,148,0.3);
        }
        .upload-hero h1 { margin: 0; font-size: 1.9rem; font-weight: 800; }
        .upload-hero p  { margin: 0.4rem 0 0; opacity: .75; font-size: 0.95rem; }

        /* Drop zone */
        .drop-zone {
            border: 2.5px dashed #013494;
            border-radius: 20px;
            padding: 2.5rem 2rem;
            text-align: center;
            background: linear-gradient(135deg, #f0f7ff 0%, #e8f0fe 100%);
            color: #013494;
            font-weight: 600;
            font-size: 1.05rem;
            margin-bottom: 1rem;
        }
        .drop-zone .drop-icon { font-size: 2.8rem; display: block; margin-bottom: 0.5rem; }
        .drop-zone .drop-hint { font-size: 0.82rem; font-weight: 400; opacity: 0.65; margin-top: 0.35rem; }

        /* Schema badge pill */
        .schema-pill {
            display: inline-block;
            background: #e8f0fe;
            color: #013494;
            border-radius: 20px;
            padding: 0.2rem 0.75rem;
            font-size: 0.78rem;
            font-weight: 600;
            margin: 0.2rem 0.15rem;
            border: 1px solid #b3ccf8;
        }

        /* KPI row */
        .kpi-box {
            background: linear-gradient(135deg, #013494 0%, #0252cc 100%);
            border-radius: 16px;
            padding: 1.3rem 1.5rem;
            color: white;
            box-shadow: 0 4px 20px rgba(1,52,148,0.22);
            text-align: center;
        }
        .kpi-box .kpi-icon  { font-size: 1.6rem; }
        .kpi-box .kpi-val   { font-size: 1.85rem; font-weight: 800; margin: 0.2rem 0; }
        .kpi-box .kpi-label { font-size: 0.78rem; opacity: 0.75; text-transform: uppercase; letter-spacing: 0.06em; }

        /* Sidebar */
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #013494 0%, #0a2d6e 100%);
            color: white;
        }
        section[data-testid="stSidebar"] * { color: white !important; }
        section[data-testid="stSidebar"] hr { border-color: rgba(255,255,255,0.2); }

        /* Validation */
        .val-error { background:#fff1f2; border-left:4px solid #ef4444; border-radius:6px; padding:0.6rem 1rem; margin-bottom:0.5rem; font-size:0.88rem; color:#991b1b; }
        .val-ok    { background:#f0fdf4; border-left:4px solid #22c55e; border-radius:6px; padding:0.6rem 1rem; margin-bottom:0.5rem; font-size:0.88rem; color:#166534; }
    </style>
    """,
    unsafe_allow_html=True,
)


# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Upload Controls")
    st.markdown("---")
    st.markdown("**Expected schema**")
    pills_html = "".join(f'<span class="schema-pill">{c}</span>' for c in REQUIRED_COLUMNS)
    st.markdown(pills_html, unsafe_allow_html=True)
    st.markdown("---")

    if "wo_df" in st.session_state and st.session_state.wo_df is not None:
        df_cached = st.session_state.wo_df
        st.success(f"✅ {len(df_cached):,} rows loaded")
        st.markdown(f"**File:** `{st.session_state.get('wo_filename', 'unknown')}`")
        if st.button("🗑️ Clear uploaded data", key="clear_data"):
            st.session_state.wo_df       = None
            st.session_state.wo_filename = None
            st.rerun()
    else:
        st.info("No data loaded yet.")

    st.markdown("---")
    st.caption("Riseboro Predictive Analytics v1.0")


# ─────────────────────────────────────────────────────────────────────────────
# HERO
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="upload-hero">
        <h1>📂 Work Order Data Upload</h1>
        <p>Import your work-order CSV to populate the analytics dashboard with live data.</p>
    </div>
    """,
    unsafe_allow_html=True,
)


# ─────────────────────────────────────────────────────────────────────────────
# HELPER FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────
def _parse_and_validate(uploaded):
    """Read CSV, coerce types, return (df, errors). Empty errors list = success."""
    errors = []
    try:
        df = pd.read_csv(uploaded)
    except Exception as exc:
        return None, [f"Could not parse file: {exc}"]

    df.columns = df.columns.str.strip()

    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        errors.append(f"Missing column(s): {', '.join(missing)}")

    extra = [c for c in df.columns if c not in REQUIRED_COLUMNS]
    if extra:
        errors.append(f"Unexpected column(s): {', '.join(extra)} (will be kept)")

    if missing:
        return df, errors

    for col in DATE_COLS:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    for col in NUMERIC_COLS:
        if col in df.columns:
            df[col] = (
                df[col].astype(str)
                .str.replace(r"[$,]", "", regex=True)
                .pipe(pd.to_numeric, errors="coerce")
            )

    return df, errors


def _kpi_box(icon, value, label):
    st.markdown(
        f"""
        <div class="kpi-box">
            <div class="kpi-icon">{icon}</div>
            <div class="kpi-val">{value}</div>
            <div class="kpi-label">{label}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────────────────────────────────────
# UPLOAD ZONE
# ─────────────────────────────────────────────────────────────────────────────
section_header("☁️ Upload CSV", "Drop your work-order export here")
divider()

st.markdown(
    """
    <div class="drop-zone">
        <span class="drop-icon">📂</span>
        Drag &amp; drop your <strong>work order CSV</strong> here, or click <em>Browse files</em> below.
        <div class="drop-hint">Supported format: .csv &nbsp;·&nbsp; Max size: 200 MB</div>
    </div>
    """,
    unsafe_allow_html=True,
)

uploaded_file = st.file_uploader(
    "Choose a CSV file",
    type=["csv"],
    label_visibility="collapsed",
    key="wo_uploader",
)


# ─────────────────────────────────────────────────────────────────────────────
# PROCESS UPLOAD
# ─────────────────────────────────────────────────────────────────────────────
if uploaded_file is not None:
    with st.spinner("Parsing and validating your file…"):
        df, errors = _parse_and_validate(uploaded_file)

    non_fatal = [e for e in errors if "Unexpected" in e]
    fatal     = [e for e in errors if "Unexpected" not in e]

    if fatal:
        for err in fatal:
            st.markdown(f'<div class="val-error">⚠️ {err}</div>', unsafe_allow_html=True)
        st.error("Upload failed — please fix the errors above and re-upload.")

    else:
        st.session_state.wo_df       = df
        st.session_state.wo_filename = uploaded_file.name

        st.markdown('<div class="val-ok">✅ File validated successfully — all required columns present.</div>', unsafe_allow_html=True)
        for w in non_fatal:
            st.warning(w)

        st.markdown("<br>", unsafe_allow_html=True)

        # KPI SUMMARY
        section_header("📊 Quick Summary", f"Loaded from `{uploaded_file.name}`")
        divider()

        total_rows  = len(df)
        total_spend = df["Total"].sum() if "Total" in df.columns else 0
        unique_bldg = df["Building"].nunique() if "Building" in df.columns else 0
        unique_emp  = df["Employee"].nunique() if "Employee" in df.columns else 0

        k1, k2, k3, k4 = st.columns(4)
        with k1:
            _kpi_box("📋", f"{total_rows:,}", "Work Orders")
        with k2:
            _kpi_box("💰", f"${total_spend:,.2f}", "Total Spend")
        with k3:
            _kpi_box("🏢", str(unique_bldg), "Buildings")
        with k4:
            _kpi_box("👷", str(unique_emp), "Employees")

        st.markdown("<br>", unsafe_allow_html=True)

        # STATUS BREAKDOWN
        if "Status" in df.columns:
            section_header("🔵 Status Breakdown")
            divider()

            status_counts = df["Status"].value_counts().reset_index()
            status_counts.columns = ["Status", "Count"]

            s_cols = st.columns(min(len(status_counts), 5))
            for i, row in status_counts.iterrows():
                with s_cols[i % len(s_cols)]:
                    st.metric(label=str(row["Status"]), value=int(row["Count"]))

            st.markdown("<br>", unsafe_allow_html=True)

        # DATA PREVIEW
        section_header("📋 Data Preview")
        divider()

        search = st.text_input(
            "Filter rows",
            placeholder="Search by WO, building, employee, status…",
            label_visibility="collapsed",
            key="wo_search",
        )

        filtered_df = df.copy()
        if search.strip():
            mask = filtered_df.apply(
                lambda col: col.astype(str).str.contains(search.strip(), case=False, na=False)
            ).any(axis=1)
            filtered_df = filtered_df[mask]

        st.caption(f"Showing {len(filtered_df):,} of {total_rows:,} rows")

        col_config = {
            "WO":                st.column_config.TextColumn("WO #", pinned=True),
            "Prop-Unit":         st.column_config.TextColumn("Prop-Unit"),
            "Building":          st.column_config.TextColumn("Building"),
            "Status":            st.column_config.TextColumn("Status"),
            "Call Date":         st.column_config.DatetimeColumn("Call Date",  format="MMM DD, YYYY"),
            "Start Date":        st.column_config.DatetimeColumn("Start Date", format="MMM DD, YYYY"),
            "Employee":          st.column_config.TextColumn("Employee"),
            "Brief Desc":        st.column_config.TextColumn("Brief Desc"),
            "Quantity":          st.column_config.NumberColumn("Qty",         format="%d"),
            "Stock":             st.column_config.TextColumn("Stock"),
            "Stock Description": st.column_config.TextColumn("Stock Description"),
            "Unit Price":        st.column_config.NumberColumn("Unit Price",  format="$%.2f"),
            "Total":             st.column_config.NumberColumn("Total",       format="$%.2f"),
        }

        st.dataframe(
            filtered_df,
            column_config=col_config,
            hide_index=True,
            height=420,
        )

        st.markdown("<br>", unsafe_allow_html=True)

        # SPEND BY BUILDING
        if "Building" in df.columns and "Total" in df.columns:
            section_header("🏢 Spend by Building")
            divider()

            spend_by_bldg = (
                df.groupby("Building")["Total"]
                .sum()
                .sort_values(ascending=False)
                .head(15)
                .reset_index()
            )
            spend_by_bldg.columns = ["Building", "Total Spend"]
            st.bar_chart(spend_by_bldg, x="Building", y="Total Spend",
                         x_label="Building", y_label="Total Spend ($)")

        # DOWNLOAD
        st.markdown("<br>", unsafe_allow_html=True)
        section_header("⬇️ Export")
        divider()

        csv_bytes = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="⬇️ Download cleaned CSV",
            data=csv_bytes,
            file_name=f"cleaned_{uploaded_file.name}",
            mime="text/csv",
            key="download_cleaned",
        )

else:
    # EMPTY STATE
    if "wo_df" in st.session_state and st.session_state.wo_df is not None:
        st.info("Previously uploaded data is still available in session. Upload a new file above or clear it from the sidebar.")
    else:
        st.markdown("<br>", unsafe_allow_html=True)
        section_header("📋 Expected Column Schema")
        divider()
        st.markdown(
            "Your CSV must contain **exactly** the following columns "
            "(additional columns are allowed but will be flagged):"
        )
        schema_df = pd.DataFrame(
            {
                "Column": REQUIRED_COLUMNS,
                "Type": [
                    "Text", "Text", "Text", "Text",
                    "Date", "Date",
                    "Text", "Text",
                    "Number", "Text", "Text", "Currency", "Currency",
                ],
                "Example": [
                    "WO-10042", "12A", "Saratoga Ave", "Open",
                    "2024-01-15", "2024-01-16",
                    "John Smith", "Replace HVAC filter",
                    "2", "SKU-9981", "HVAC Filter 16x20", "$12.50", "$25.00",
                ],
                "Required": ["✅"] * len(REQUIRED_COLUMNS),
            }
        )
        st.dataframe(
            schema_df,
            column_config={
                "Column":   st.column_config.TextColumn("Column"),
                "Type":     st.column_config.TextColumn("Data Type"),
                "Example":  st.column_config.TextColumn("Example Value"),
                "Required": st.column_config.TextColumn("Required"),
            },
            hide_index=True,
        )
