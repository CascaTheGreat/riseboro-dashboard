# Integrate Analysis Helpers into Dashboard (Per-Unit)

The `src/analysis/` module contains three powerful helpers — [trends.py](file:///Users/leoledlow/Projects/riseboro_streamlit/src/analysis/trends.py), [hotspots.py](file:///Users/leoledlow/Projects/riseboro_streamlit/src/analysis/hotspots.py), and [significance.py](file:///Users/leoledlow/Projects/riseboro_streamlit/src/analysis/significance.py) — that are currently unused by the Streamlit dashboard. These operate on an enriched dataset with columns like `source_property`, `prop_unit`, `final_category`, `ttl_days`, `call_date`, `Year`, `Month`, `Month_Num`, and `status`. The dashboard's work-order data (via upload) has a different column schema (`Building`, `Prop-Unit`, `Call Date`, `Brief Desc`, `issue_category`, `Status`). This plan bridges that gap and adds a dedicated **per-unit analytics** section to [home.py](file:///Users/leoledlow/Projects/riseboro_streamlit/pages/home.py).

## User Review Required

> [!IMPORTANT]
> **Column mapping assumption.** The analysis helpers expect columns like `source_property`, `prop_unit`, `final_category`, `ttl_days`, and `Month`. The dashboard data has `Building`, `Prop-Unit`, `issue_category`, and no `ttl_days` (resolution time). The plan introduces an adapter layer to rename columns, but **resolution-time metrics will show "N/A"** unless your CSV includes start/completion dates that let us compute duration. Is that acceptable, or do you have a column for resolution time?

> [!WARNING]
> **`scipy` dependency.** The `significance.py` module requires `scipy` for `stats.linregress` and `stats.chisquare`. Verify it's in your `venv` — if not, we'll add it to `requirements.txt`.

## Open Questions

1. **Resolution time** — Does your uploaded CSV have a completion/close date column we can use to compute `ttl_days`? If not, we'll skip the "Avg Resolution (Days)" metric from hotspots and show WO count + category mix only.

2. **Unit filter scope** — Should the new per-unit section respect the existing sidebar filters (date range, building, status) or always analyze the full raw dataset? The current high-volume tables use `recent_raw` (unfiltered, last 3 years). I'd recommend the same approach for consistency.

3. **New page vs. section** — Should this be a new page (e.g., `pages/unit_analysis.py`) or a new section appended to the existing home dashboard? I'm proposing it as a collapsible section at the bottom of `home.py`, but a separate page keeps the home page lighter.

## Proposed Changes

### Adapter Layer

#### [NEW] [`src/analysis/adapter.py`](file:///Users/leoledlow/Projects/riseboro_streamlit/src/analysis/adapter.py)

A thin adapter that renames dashboard columns to match the analysis module's expected schema, enabling the helpers to be called without modifying their internals.

| Dashboard Column | Analysis Column | Notes |
|---|---|---|
| `Building` | `source_property` | YARDI property code |
| `Prop-Unit` | `prop_unit` | Unit identifier |
| `issue_category` | `final_category` | Category label |
| `Call Date` | `call_date` | Already datetime |
| `Status` | `status` | WO status |
| `Brief Desc` | `description` | Free-text desc |

The adapter will:
- Rename the columns above
- Add `Year`, `Month_Num`, `Month` via `trends.add_time_parts()`
- Compute `ttl_days` from `Start Date` → `Call Date` if both exist, else set to `NaN`
- Return a DataFrame compatible with all three analysis modules

---

### Dashboard Integration

#### [MODIFY] [`pages/home.py`](file:///Users/leoledlow/Projects/riseboro_streamlit/pages/home.py)

Add a new **"Unit-Level Analytics"** section between the existing "High-Volume Tracking" section and the "Volume & Status" section (~line 771). This section will contain:

**1. Unit Hotspot Summary (from `hotspots.py`)**
- KPI row: total apartment units analyzed, avg WOs/unit (portfolio-wide), top-10% avg WOs/unit
- Uses `hotspots.exclude_non_apartments()` → `hotspots.compare_groups()` to show a 3-row comparison table (All Units vs Top 10% vs Top 10)

**2. Top Hotspot Units Table (from `hotspots.py`)**
- `hotspots.top_units_detail(df, n=15)` rendered as an `st.dataframe` with column configs
- Columns: Unit, Property, Total WOs, Avg Resolution (Days), Primary Issue (Share %)
- Joined with `bldg_info` for address/project context

**3. Per-Unit Trend Charts (from `trends.py`)**
- A `st.selectbox` to pick a specific unit from the top hotspot list
- For the selected unit:
  - **Yearly WO count** line chart via `trends.yearly_counts()` — shows whether the unit's volume is growing or stable
  - **Monthly seasonality** bar chart via `trends.monthly_counts(fill_missing=True)` — shows which months are peak

**4. Trend Significance Badges (from `significance.py`)**
- For the selected unit (if it has ≥3 years of data):
  - `significance.yearly_trend()` → display slope, p-value, and a 🔴/🟢 badge for statistically significant increasing/decreasing trend
  - `significance.seasonality()` → display chi² p-value and a badge if seasonality is statistically significant
  - `significance.month_outliers()` → list months that are statistically above/below the uniform expectation

---

### Config / Dependencies

#### [MODIFY] [`src/config.py`](file:///Users/leoledlow/Projects/riseboro_streamlit/src/config.py)

No changes needed — `MONTH_MAP` and `MONTH_NAMES` are already exported and will be used by the adapter.

#### [VERIFY] `requirements.txt`

Confirm `scipy` is listed. If not, add it.

## Verification Plan

### Automated Tests
```bash
# Verify scipy is importable
cd /Users/leoledlow/Projects/riseboro_streamlit && source venv/bin/activate && python -c "from scipy import stats; print('scipy OK')"

# Verify adapter module imports cleanly
python -c "from src.analysis.adapter import adapt_for_analysis; print('adapter OK')"
```

### Manual Verification
- Load the app at `http://localhost:8501`, upload work-order data, navigate to the home dashboard
- Scroll to the new "Unit-Level Analytics" section
- Verify the hotspot summary table renders with meaningful numbers
- Select a top unit from the dropdown and confirm the yearly + monthly charts render
- Verify significance badges appear for units with sufficient data
- Confirm existing dashboard sections are unaffected
