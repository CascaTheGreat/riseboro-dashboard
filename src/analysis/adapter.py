"""
src/analysis/adapter.py
-----------------------
Adapter layer that normalizes Streamlit dashboard work-order data into the schema
expected by the src/analysis helper modules (trends.py, hotspots.py, significance.py).
"""

from __future__ import annotations

import pandas as pd
import numpy as np
from src.config import MONTH_MAP, MONTH_NAMES


def adapt_for_analysis(df: pd.DataFrame, building_info: pd.DataFrame | None = None) -> pd.DataFrame:
    """
    Transform dashboard DataFrame into the standardized schema for analysis modules:
      - source_property (from Building)
      - property_name (from bc_PROJECT_NAME or PLACE_NAME or Building)
      - prop_unit (from Prop-Unit)
      - final_category (from issue_category / Brief Desc)
      - call_date (from Call Date)
      - status (from Status)
      - description (from Brief Desc)
      - ttl_days (from Start Date - Call Date, clipped [0, 365])
      - Year, Month_Num, Month (derived from call_date)
    """
    if df is None or df.empty:
        return pd.DataFrame()

    out = df.copy()

    # Column mappings
    rename_map = {}
    if "Building" in out.columns:
        rename_map["Building"] = "source_property"
    if "Prop-Unit" in out.columns:
        rename_map["Prop-Unit"] = "prop_unit"
    if "issue_category" in out.columns:
        rename_map["issue_category"] = "final_category"
    if "Call Date" in out.columns:
        rename_map["Call Date"] = "call_date"
    if "Status" in out.columns:
        rename_map["Status"] = "status"
    if "Brief Desc" in out.columns:
        rename_map["Brief Desc"] = "description"

    out = out.rename(columns=rename_map)

    # Ensure required columns exist
    if "source_property" not in out.columns:
        out["source_property"] = "Unknown"
    if "prop_unit" not in out.columns:
        out["prop_unit"] = "Unknown"
    if "final_category" not in out.columns:
        out["final_category"] = "Other"

    # Derive property_name for display
    if "bc_PROJECT_NAME" in out.columns and out["bc_PROJECT_NAME"].notna().any():
        out["property_name"] = out["bc_PROJECT_NAME"].fillna(out["source_property"])
    elif "bc_PLACE_NAME" in out.columns and out["bc_PLACE_NAME"].notna().any():
        out["property_name"] = out["bc_PLACE_NAME"].fillna(out["source_property"])
    else:
        out["property_name"] = out["source_property"]

    # Normalize Dates and add Year, Month_Num, Month
    if "call_date" in out.columns:
        out["call_date"] = pd.to_datetime(out["call_date"], errors="coerce")
        out["Year"] = out["call_date"].dt.year.astype("Int64")
        out["Month_Num"] = out["call_date"].dt.month
        out["Month"] = out["Month_Num"]  # significance.seasonality expects 'Month'
    else:
        out["call_date"] = pd.NaT
        out["Year"] = pd.Series(dtype="Int64")
        out["Month_Num"] = pd.Series(dtype="float")
        out["Month"] = pd.Series(dtype="float")

    # Compute resolution duration in days (ttl_days)
    # Using Start Date and Call Date
    start_col = "Start Date" if "Start Date" in out.columns else ("start_date" if "start_date" in out.columns else None)
    if start_col and "call_date" in out.columns:
        start_dates = pd.to_datetime(out[start_col], errors="coerce")
        diff_days = (start_dates - out["call_date"]).dt.total_seconds() / 86400.0
        # If diff is negative, set to 0; if exceeds a year (365 days), consider resolved / cap at 365 days
        diff_days = diff_days.mask(diff_days < 0, 0)
        diff_days = diff_days.mask(diff_days > 365, 365)
        out["ttl_days"] = diff_days
    else:
        out["ttl_days"] = np.nan

    return out
