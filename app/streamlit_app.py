# app/streamlit_app.py
"""
Interactive Streamlit dashboard for Ola Ride Insights
- Dashboard (KPIs + plots)
- Screenshots & Insights (read-only from docs/figures + docs/figures/insights.json)
- SQL Runner (in-memory SQLite)
- About
"""

from pathlib import Path
import json
import sqlite3
from typing import Dict

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

# -----------------------------------------------------------------------------
# Page config
# -----------------------------------------------------------------------------
st.set_page_config(page_title="Ola Ride Insights", layout="wide")

# -----------------------------------------------------------------------------
# Paths
# -----------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[1]         # project root
DATA_DIR = ROOT / "data"
FIG_DIR = ROOT / "docs" / "figures"
LOGO_DIR = FIG_DIR / "logos"                       # <-- your logos folder
INSIGHTS_JSON = FIG_DIR / "insights.json"          # optional
PBI_PDF = FIG_DIR / "ola_ride_insights.pdf"  # <-- add this

# Prefer cleaned dataset
CLEANED_WITH_CANCEL = DATA_DIR / "ola_cleaned_with_cancellations.csv"
CLEANED = DATA_DIR / "ola_cleaned.csv"
FULL = DATA_DIR / "ola_full.csv"
SAMPLE = DATA_DIR / "ola_sample.csv"  # optional fallback

# -----------------------------------------------------------------------------
# Data loading
# -----------------------------------------------------------------------------
def load_data(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(path)

    # robust CSV read
    try:
        df = pd.read_csv(path, low_memory=False)
    except Exception:
        df = pd.read_csv(path, engine="python", on_bad_lines="skip")

    # normalize column names
    df.columns = [str(c).strip().replace("\ufeff", "") for c in df.columns]

    # create Datetime if needed
    if "Datetime" not in df.columns:
        if "Date" in df.columns and "Time" in df.columns:
            df["Datetime"] = pd.to_datetime(
                df["Date"].astype(str).str.strip() + " " + df["Time"].astype(str).str.strip(),
                errors="coerce",
            )
        elif "Date" in df.columns:
            df["Datetime"] = pd.to_datetime(df["Date"].astype(str).str.strip(), errors="coerce")
        else:
            df["Datetime"] = pd.NaT
    else:
        try:
            df["Datetime"] = pd.to_datetime(df["Datetime"], errors="coerce")
        except Exception:
            pass

    # numeric coercions
    for col in ["Booking_Value", "Ride_Distance", "Driver_Ratings", "Customer_Rating", "V_TAT", "C_TAT"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # normalize Booking_Status capitalization
    if "Booking_Status" in df.columns:
        df["Booking_Status"] = df["Booking_Status"].astype(str).str.strip().str.title()

    # derived features
    if "ride_hour" not in df.columns:
        try:
            df["ride_hour"] = df["Datetime"].dt.hour
        except Exception:
            df["ride_hour"] = pd.NA

    if "day_of_week" not in df.columns:
        try:
            df["day_of_week"] = df["Datetime"].dt.day_name()
        except Exception:
            df["day_of_week"] = pd.NA

    if "ride_duration" not in df.columns:
        if "V_TAT" in df.columns or "C_TAT" in df.columns:
            v = pd.to_numeric(df.get("V_TAT", 0)).fillna(0)
            c = pd.to_numeric(df.get("C_TAT", 0)).fillna(0)
            df["ride_duration"] = v + c
        else:
            df["ride_duration"] = pd.NA

    # is_peak heuristic (7–10, 17–20)
    if "is_peak" not in df.columns:
        def _is_peak(h):
            if pd.isna(h):
                return 0
            h = int(h)
            return 1 if (7 <= h <= 10 or 17 <= h <= 20) else 0
        df["is_peak"] = df["ride_hour"].apply(_is_peak)

    return df


# choose dataset
if CLEANED_WITH_CANCEL.exists():
    DATA_PATH = CLEANED_WITH_CANCEL
elif CLEANED.exists():
    DATA_PATH = CLEANED
elif FULL.exists():
    DATA_PATH = FULL
elif SAMPLE.exists():
    DATA_PATH = SAMPLE
else:
    DATA_PATH = None

# load data
try:
    df = load_data(DATA_PATH)
except Exception as e:
    st.exception(f"Failed to load dataset: {e}")
    st.stop()


# -----------------------------------------------------------------------------
# Helpers / cache
# -----------------------------------------------------------------------------
@st.cache_data
def get_basic_stats(data: pd.DataFrame) -> Dict:
    stats = {
        "rows": len(data),
        "cols": data.shape[1],
        "start_date": None,
        "end_date": None,
    }
    if "Datetime" in data.columns and not data["Datetime"].dropna().empty:
        stats["start_date"] = str(data["Datetime"].dropna().min().date())
        stats["end_date"] = str(data["Datetime"].dropna().max().date())
    return stats

basic_stats = get_basic_stats(df)

# collect logos (optional)
logo_files = {}
if LOGO_DIR.exists():
    for p in LOGO_DIR.iterdir():
        if p.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif", ".svg"}:
            logo_files[p.stem.lower()] = p

# -----------------------------------------------------------------------------
# Sidebar: navigation + filters
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("## Dataset")
    st.write(f"Loaded: `{DATA_PATH.name}`")
    st.write(f"Rows: **{basic_stats['rows']:,}** • Columns: **{basic_stats['cols']}**")
    if basic_stats.get("start_date"):
        st.write(f"Range: {basic_stats['start_date']} → {basic_stats['end_date']}")

    st.markdown("---")
    st.markdown("## Navigation")
    PAGE = st.radio("Go to", ["Dashboard", "Power BI (PDF)", "Screenshots & Insights", "SQL Runner", "About"])

    st.markdown("---")
    st.markdown("## Filters")

    # date range
    try:
        min_date = df["Datetime"].dropna().min().date()
        max_date = df["Datetime"].dropna().max().date()
    except Exception:
        min_date = pd.to_datetime("2020-01-01").date()
        max_date = pd.to_datetime("2025-12-31").date()
    date_range = st.date_input("Date range", [min_date, max_date])

    # vehicle & payment options
    vehicle_options = list(df["Vehicle_Type"].dropna().unique()) if "Vehicle_Type" in df.columns else []
    payment_options = list(df["Payment_Method"].dropna().unique()) if "Payment_Method" in df.columns else []

    vehicle_types = st.multiselect(
        "Vehicle type", options=vehicle_options, default=vehicle_options[:5] if vehicle_options else []
    )
    payment_methods = st.multiselect(
        "Payment method", options=payment_options, default=payment_options if payment_options else []
    )

# apply filters
mask = pd.Series(True, index=df.index)
if "Datetime" in df.columns:
    try:
        mask &= df["Datetime"].dt.date >= date_range[0]
        mask &= df["Datetime"].dt.date <= date_range[1]
    except Exception:
        pass
if vehicle_types and "Vehicle_Type" in df.columns:
    mask &= df["Vehicle_Type"].isin(vehicle_types)
if payment_methods and "Payment_Method" in df.columns:
    mask &= df["Payment_Method"].isin(payment_methods)

df_f = df.loc[mask].copy()

# -----------------------------------------------------------------------------
# Small plotting helpers
# -----------------------------------------------------------------------------
def plt_line_rides_by_date(data: pd.DataFrame):
    if "Datetime" not in data.columns or data["Datetime"].dropna().empty:
        st.info("No valid Datetime for time-series.")
        return
    rides_by_date = data.groupby(data["Datetime"].dt.date).size().rename("count")
    rides_by_date.index = pd.to_datetime(rides_by_date.index)
    fig, ax = plt.subplots(figsize=(10, 3))
    ax.plot(rides_by_date.index, rides_by_date.values, marker="o", linewidth=1)
    ax.set_title("Daily Ride Volume")
    ax.set_ylabel("Rides")
    ax.grid(alpha=0.3)
    st.pyplot(fig)


def plt_bar_rides_by_hour(data: pd.DataFrame):
    if "ride_hour" not in data.columns or data["ride_hour"].dropna().empty:
        st.info("No ride_hour info.")
        return
    hours = data["ride_hour"].dropna().astype(int).value_counts().sort_index()
    fig, ax = plt.subplots(figsize=(10, 3))
    ax.bar(hours.index, hours.values)
    ax.set_xlabel("Hour (0-23)")
    ax.set_ylabel("Ride Count")
    ax.set_title("Rides by Hour of Day")
    st.pyplot(fig)


def plt_revenue_by_payment(data: pd.DataFrame):
    if "Payment_Method" not in data.columns or "Booking_Value" not in data.columns:
        st.info("Payment_Method or Booking_Value missing.")
        return
    # normalize minor label variants
    tmp = data.copy()
    tmp["Payment_Method"] = tmp["Payment_Method"].astype(str).str.strip().str.replace(r"\s+", " ", regex=True)
    rev = tmp.groupby("Payment_Method")["Booking_Value"].sum().sort_values(ascending=False)
    fig, ax = plt.subplots(figsize=(6, 3))
    ax.bar(rev.index.astype(str), rev.values)
    ax.set_title("Total Booking Value by Payment Method")
    ax.set_ylabel("Total Booking Value")
    ax.set_xticklabels(rev.index, rotation=30, ha="right")
    st.pyplot(fig)


def plt_cancellations_by_vehicle(data: pd.DataFrame):
    if "Booking_Status" not in data.columns or "Vehicle_Type" not in data.columns:
        st.info("Booking_Status or Vehicle_Type missing.")
        return
    cancelled = data.loc[data["Booking_Status"] != "Success"]
    if cancelled.empty:
        st.info("No cancellations in filtered data")
        return
    grouped = cancelled.groupby(["Vehicle_Type", "Booking_Status"]).size().unstack(fill_value=0)
    fig, ax = plt.subplots(figsize=(9, 3))
    grouped.plot(kind="bar", ax=ax)
    ax.set_title("Cancellations by Vehicle Type")
    ax.set_ylabel("count")
    st.pyplot(fig)


def plt_cancellations_by_hour(data: pd.DataFrame):
    if "Booking_Status" not in data.columns or "ride_hour" not in data.columns:
        st.info("Booking_Status or ride_hour missing.")
        return
    cancelled = data.loc[data["Booking_Status"] != "Success"]
    if cancelled.empty:
        st.info("No cancellations in filtered data")
        return
    grouped = cancelled.groupby(["ride_hour", "Booking_Status"]).size().unstack(fill_value=0).sort_index()
    fig, ax = plt.subplots(figsize=(10, 3))
    grouped.plot(kind="bar", stacked=False, ax=ax)
    ax.set_title("Cancellations by Hour of Day")
    ax.set_xlabel("Hour")
    st.pyplot(fig)


# -----------------------------------------------------------------------------
# Load insights (optional)
# -----------------------------------------------------------------------------
insights_map: Dict[str, str | Dict] = {}
if INSIGHTS_JSON.exists():
    try:
        with open(INSIGHTS_JSON, "r", encoding="utf-8") as f:
            raw = json.load(f)
            # allow either a mapping or a single string
            insights_map = raw if isinstance(raw, dict) else {}
    except Exception:
        insights_map = {}

# -----------------------------------------------------------------------------
# SQLite helper for SQL Runner
# -----------------------------------------------------------------------------
def load_sqlite(df_local: pd.DataFrame):
    conn_local = sqlite3.connect(":memory:")
    safe_df = df_local.copy()
    # SQL-friendly column names
    safe_df.columns = [str(c).replace("-", "_").replace(" ", "_") for c in safe_df.columns]
    safe_df.to_sql("ola_rides", conn_local, index=False, if_exists="replace")
    return conn_local

# -----------------------------------------------------------------------------
# Prepared SQL queries (safer variants)
# -----------------------------------------------------------------------------
PREPARED_QUERIES = [
    ("1 - All successful bookings",
     "SELECT * FROM ola_rides WHERE Booking_Status = 'Success' LIMIT 100;"),

    ("2 - Avg ride distance by vehicle type",
     "SELECT Vehicle_Type, AVG(Ride_Distance) AS avg_distance "
     "FROM ola_rides GROUP BY Vehicle_Type ORDER BY avg_distance DESC;"),

    ("3 - Total number of cancelled rides by customers",
     "SELECT COUNT(*) AS cancelled_by_customer "
     "FROM ola_rides "
     "WHERE Booking_Status IN ('Canceled By Customer','Cancelled By Customer');"),

    ("4 - Top 5 customers (by booking count)",
     "SELECT Customer_ID, COUNT(*) AS cnt "
     "FROM ola_rides GROUP BY Customer_ID "
     "ORDER BY cnt DESC LIMIT 5;"),

    ("5 - Driver cancellations for 'Personal & Car related issue'",
     "SELECT COUNT(*) AS cnt FROM ola_rides "
     "WHERE Canceled_Rides_by_Driver = 'Personal & Car related issue';"),

    ("6 - Max/Min driver ratings for Prime Sedan",
     "SELECT MAX(Driver_Ratings) AS max_rating, MIN(Driver_Ratings) AS min_rating "
     "FROM ola_rides WHERE Vehicle_Type = 'Prime Sedan';"),

    ("7 - All rides paid with UPI",
     "SELECT * FROM ola_rides WHERE Payment_Method LIKE '%UPI%' LIMIT 200;"),

    ("8 - Avg customer rating per vehicle type",
     "SELECT Vehicle_Type, AVG(Customer_Rating) AS avg_customer_rating "
     "FROM ola_rides GROUP BY Vehicle_Type ORDER BY avg_customer_rating DESC;"),

    ("9 - Total booking value of successful rides",
     "SELECT SUM(Booking_Value) AS total_success_revenue "
     "FROM ola_rides WHERE Booking_Status = 'Success';"),

    ("10 - List all incomplete rides with reasons",
     "SELECT Booking_ID, Incomplete_Rides, Incomplete_Rides_Reason "
     "FROM ola_rides WHERE Incomplete_Rides IN ('Yes','yes') LIMIT 200;"),
]

# -----------------------------------------------------------------------------
# PAGES
# -----------------------------------------------------------------------------
if PAGE == "Dashboard":
    # Header with logos
    colL, colC, colR = st.columns([1, 6, 1])
    with colL:
        if "ola_logo" in logo_files:
            st.image(str(logo_files["ola_logo"]), width=120)
    with colC:
        st.markdown("<h1 style='margin:0;'>Interactive EDA & Dashboard</h1>", unsafe_allow_html=True)
        st.caption("Explore dataset filters, run SQL queries, and view saved EDA figures.")
    with colR:
        names = ["sedan", "mini", "suv", "ebike"]
        cols = st.columns(len(names))
        for i, nm in enumerate(names):
            if nm in logo_files:
                cols[i].image(str(logo_files[nm]), width=56)

    st.markdown("---")

    # KPIs
    k1, k2, k3, k4 = st.columns(4)
    total_rides = len(df_f)
    success_count = int(df_f["Booking_Status"].eq("Success").sum()) if "Booking_Status" in df_f.columns else 0
    cancelled_count = total_rides - success_count
    total_revenue = float(df_f["Booking_Value"].sum()) if "Booking_Value" in df_f.columns else 0.0
    avg_driver_rating = float(df_f["Driver_Ratings"].mean()) if "Driver_Ratings" in df_f.columns else np.nan

    def kpi_card_html(label, value, bg):
        return f"""
        <div style="background:{bg};padding:12px;border-radius:10px;color:white;">
            <div style="font-size:12px;opacity:0.9">{label}</div>
            <div style="font-size:20px;font-weight:700;margin-top:6px">{value}</div>
        </div>
        """

    k1.markdown(kpi_card_html("Total rides (filtered)", f"{total_rides:,}", "#198754"), unsafe_allow_html=True)
    k2.markdown(kpi_card_html("Successful rides", f"{success_count:,}", "#0d6efd"), unsafe_allow_html=True)
    k3.markdown(kpi_card_html("Total booking value", f"₹{total_revenue:,.2f}", "#ff9100"), unsafe_allow_html=True)
    k4.markdown(
        kpi_card_html("Avg Driver Rating", f"{avg_driver_rating:.2f}" if not np.isnan(avg_driver_rating) else "N/A", "#6f42c1"),
        unsafe_allow_html=True,
    )

    st.markdown("---")
    # two columns
    left, right = st.columns([2, 1])
    with left:
        plt_line_rides_by_date(df_f)
        st.markdown("**Rides by day** — steady baseline; check end-of-period dips for partial data.")
    with right:
        plt_revenue_by_payment(df_f)
        st.markdown("**Revenue by payment method** — cash & UPI dominate total booking value.")

    st.markdown("---")
    st.subheader("Time & demand patterns")
    plt_bar_rides_by_hour(df_f)

    st.markdown("---")
    st.subheader("Cancellations (breakdowns)")
    plt_cancellations_by_vehicle(df_f)
    plt_cancellations_by_hour(df_f)

    st.markdown("---")
    st.subheader("Top customers")
    if "Customer_ID" in df_f.columns and "Booking_Value" in df_f.columns:
        top_customers = df_f.groupby("Customer_ID")["Booking_Value"].sum().nlargest(10).reset_index()
        st.table(top_customers)
    else:
        st.info("Customer_ID or Booking_Value missing for top-customers view.")

elif PAGE == "Screenshots & Insights":
    st.title("📸 Screenshots & Insights")
    st.caption("Pre-saved figures from `docs/figures/`. Insights are read from `insights.json` if available.")

    # Load insights.json if it exists
    insights = {}
    if INSIGHTS_JSON.exists():
        try:
            import json
            with open(INSIGHTS_JSON, "r", encoding="utf-8") as f:
                insights = json.load(f)
        except Exception as e:
            st.error(f"Failed to load insights.json: {e}")

    # Find all PNG/JPG files in figures (excluding logos folder)
    image_files = sorted([p for p in FIG_DIR.glob("*") if p.suffix.lower() in [".png", ".jpg", ".jpeg"]])

    if not image_files:
        st.warning("⚠️ No screenshots found in `docs/figures/`.")
    else:
        for img_path in image_files:
            st.image(str(img_path), use_container_width=True)

            # Match insights if available
            caption_key = img_path.stem  # e.g. "booking_status_distribution"
            if caption_key in insights:
                st.caption(f"📌 Insight: {insights[caption_key]}")
            st.divider()

elif PAGE == "Power BI (PDF)":
    st.title("📊 Power BI Report (PDF)")
    if PBI_PDF.exists():
        size_mb = PBI_PDF.stat().st_size / (1024*1024)
        with open(PBI_PDF, "rb") as f:
            st.download_button(
                "⬇️ Download ola_ride_insights.pdf",
                data=f.read(),
                file_name="ola_ride_insights.pdf",
                mime="application/pdf",
                help=f"Size ≈ {size_mb:.1f} MB"
            )
        st.success("The Power BI report is ready to download.")
        st.caption(f"Path: {PBI_PDF}")
    else:
        st.warning("Couldn’t find docs/figures/ola_ride_insights.pdf. Place it there and refresh.")

    # logos row
    logo_paths = [LOGO_DIR / "ola_logo.png", LOGO_DIR / "sedan.png", LOGO_DIR / "mini.png", LOGO_DIR / "suv.png", LOGO_DIR / "ebike.png"]
    logos_to_show = [p for p in logo_paths if p.exists()]
    if logos_to_show:
        cols = st.columns(len(logos_to_show))
        for c, p in zip(cols, logos_to_show):
            c.image(str(p), width=100)

    # list all PNGs
    pngs = sorted(FIG_DIR.glob("*.png")) if FIG_DIR.exists() else []
    if not pngs:
        st.info("No PNG figures found in docs/figures/. Save figures from the EDA notebook to docs/figures/")
    else:
        for p in pngs:
            st.header(p.name)
            cols = st.columns([1, 3])
            # ✅ no deprecation warning
            cols[0].image(str(p), use_container_width=True)

            # insight (string or object)
            val = insights_map.get(p.name, "")
            insight = val.get("insight", val) if isinstance(val, dict) else val
            if insight:
                cols[1].markdown("**Insight:**")
                cols[1].write(insight)
            else:
                cols[1].markdown("**Insight:** _(no insight found — add notes to docs/figures/insights.json)_")

elif PAGE == "SQL Runner":
    st.title("SQL Runner (in-memory SQLite)")
    st.write("Run pre-defined queries (select one) or paste a custom SQL. The filtered dataset is loaded into an in-memory SQLite table named `ola_rides`.")

    try:
        conn = load_sqlite(df_f)
    except Exception as e:
        st.error("Failed to load data into in-memory SQLite: " + str(e))
        conn = None

    prep_labels = [q[0] for q in PREPARED_QUERIES]
    sel = st.selectbox("Select a prepared query", ["(none)"] + prep_labels)
    sample_sql = ""
    if sel != "(none)":
        idx = prep_labels.index(sel)
        sample_sql = PREPARED_QUERIES[idx][1]
        st.code(sample_sql, language="sql")

    st.markdown("Or paste custom SQL (results shown below). Note: table name is `ola_rides`.")
    custom_sql = st.text_area("SQL", value=sample_sql, height=180)

    if st.button("Run SQL"):
        if conn is None:
            st.error("No SQLite connection.")
        else:
            try:
                df_sql = pd.read_sql_query(custom_sql, conn)
                st.dataframe(df_sql, use_container_width=True)
                st.write(f"Returned rows: {len(df_sql):,}")
            except Exception as e:
                st.error(f"SQL error: {e}")

    # cleanup
    try:
        if conn is not None:
            conn.close()
    except Exception:
        pass

elif PAGE == "About":
    st.title("About — Ola Ride Insights")
    st.markdown("""
**Project:** Ola Ride Insights — EDA, SQL, Streamlit dashboard, and Power BI visuals.

**What this app contains**
- Interactive dashboard with KPIs and EDA charts (derived from `data/ola_cleaned.csv`).
- Read-only page showing saved EDA figures (docs/figures) and insights (docs/figures/insights.json).
- SQL Runner with pre-made queries and a custom SQL textbox (works against filtered data).

**Notes & Tips**
- If some charts show 'No data', widen the Date range or clear filters in the sidebar.
- Logos live in `docs/figures/logos/` with names `ola_logo.png`, `sedan.png`, `mini.png`, `suv.png`, `ebike.png`.
- The `insights.json` file is intentionally read-only in the UI to avoid accidental edits. Edit it directly in the repo if you need to change notes.

**Deliverables checklist**
- ✅ `docs/EDA.md`, `docs/EXECUTIVE_SUMMARY.md`, and figures in `docs/figures/`
- ✅ Cleaned dataset in `data/ola_cleaned.csv`
- ✅ Streamlit app in `app/streamlit_app.py`
- ✅ Power BI dashboard/screenshots in `docs/powerbi/` (optional embed)

**Tech**
- Python: pandas, numpy, matplotlib, streamlit
- SQL Runner uses in-memory SQLite with the table `ola_rides`.
""")
    if (LOGO_DIR / "ola_logo.png").exists():
        st.image(str(LOGO_DIR / "ola_logo.png"), width=140)
