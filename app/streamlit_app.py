# app/streamlit_app.py
import os
import re
import csv
import streamlit as st
import pandas as pd
import sqlite3
from pathlib import Path
from streamlit.components.v1 import html as st_html

st.set_page_config(page_title="Ola Ride Insights", layout="wide")


# ---------------- Utility & Robust CSV Loader ----------------
EXPECTED_KEYWORDS = ["booking", "date", "time", "customer", "vehicle", "booking_id"]


def detect_delimiter_and_header(path, max_lines=120):
    sample_lines = []
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        for i, line in enumerate(f):
            sample_lines.append(line)
            if i + 1 >= max_lines:
                break
    sample_text = "".join(sample_lines)

    delimiter = ","
    try:
        sniffer = csv.Sniffer()
        dialect = sniffer.sniff(sample_text)
        delimiter = dialect.delimiter
    except Exception:
        for d in [",", "\t", ";", "|"]:
            if d in sample_text:
                delimiter = d
                break

    header_index = 0
    for idx, line in enumerate(sample_lines):
        low = line.lower()
        matches = sum(1 for kw in EXPECTED_KEYWORDS if kw in low)
        if matches >= 2:
            header_index = idx
            break

    return delimiter, header_index, sample_text


def drop_garbage_columns(df: pd.DataFrame):
    to_drop = []
    for col in df.columns:
        try:
            series = df[col].dropna().astype(str).str.strip()
        except Exception:
            series = pd.Series([], dtype="object")
        if series.empty:
            to_drop.append(col)
            continue
        if (series == "").all():
            to_drop.append(col)
            continue
        uniq = series.unique()
        if len(uniq) > 0 and all(str(v).upper().startswith("#NAME") for v in uniq):
            to_drop.append(col)
            continue
        if str(col).lower().startswith("unnamed"):
            non_null_fraction = series.count() / len(df) if len(df) > 0 else 0
            if non_null_fraction < 0.1:
                to_drop.append(col)
    if to_drop:
        df = df.drop(columns=to_drop)
    return df


def load_data_safe(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"File not found: {path}")

    delim, header_idx, sample = detect_delimiter_and_header(path, max_lines=120)

    try:
        df = pd.read_csv(path, sep=delim, header=header_idx, engine="python", on_bad_lines="skip")
    except Exception:
        try:
            df = pd.read_csv(path, sep=delim, header=header_idx, on_bad_lines="skip", low_memory=False)
        except Exception:
            df = pd.read_csv(path, on_bad_lines="skip")

    df.columns = [str(c).strip().rstrip(",").replace("\ufeff", "") for c in df.columns]
    df = df.replace({"null": pd.NA, "NULL": pd.NA, "None": pd.NA, "NaN": pd.NA, "": pd.NA})
    df = drop_garbage_columns(df)

    # find date/time
    date_col = None
    for c in df.columns:
        if re.search(r"\bdate\b", str(c), flags=re.I):
            date_col = c
            break
    if date_col is None:
        for c in df.columns:
            if re.search(r"timestamp|datetime", str(c), flags=re.I):
                date_col = c
                break

    time_col = None
    for c in df.columns:
        if re.search(r"\btime\b", str(c), flags=re.I):
            time_col = c
            break

    if date_col is not None and time_col is not None:
        try:
            df["Datetime"] = pd.to_datetime(df[date_col].astype(str).str.strip() + " " + df[time_col].astype(str).str.strip(), errors="coerce")
        except Exception:
            df["Datetime"] = pd.to_datetime(df[date_col], errors="coerce")
    elif date_col is not None:
        df["Datetime"] = pd.to_datetime(df[date_col].astype(str).str.strip(), errors="coerce")
    else:
        df["Datetime"] = pd.NaT

    # numeric coercions
    for col in ["Booking_Value", "Ride_Distance", "Driver_Ratings", "Customer_Rating", "V_TAT", "C_TAT"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    if "Booking_Status" in df.columns:
        df["Booking_Status"] = df["Booking_Status"].astype(str).str.strip().str.title()

    for col in ["Customer_ID", "Booking_ID", "Vehicle_Type", "Payment_Method", "Pickup_Location", "Drop_Location"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().replace({"nan": pd.NA})

    # derived features if possible (safe and idempotent)
    if "Datetime" in df.columns:
        try:
            df["ride_hour"] = df["Datetime"].dt.hour
            df["day_of_week"] = df["Datetime"].dt.day_name()
        except Exception:
            pass

    if {"V_TAT", "C_TAT"}.intersection(set(df.columns)):
        v = pd.to_numeric(df.get("V_TAT", pd.Series(dtype="float")), errors="coerce").fillna(0)
        c = pd.to_numeric(df.get("C_TAT", pd.Series(dtype="float")), errors="coerce").fillna(0)
        df["ride_duration"] = v + c
    else:
        df["ride_duration"] = pd.NA

    # peak heuristic (7-10, 17-22)
    if "ride_hour" in df.columns:
        df["is_peak"] = df["ride_hour"].apply(lambda h: 1 if (pd.notna(h) and (7 <= int(h) <= 10 or 17 <= int(h) <= 22)) else 0)
    else:
        df["is_peak"] = 0

    return df


@st.cache_data
def load_data_cached(path: str):
    return load_data_safe(path)


# ---------------- Dataset Path (prefer cleaned) ----------------
project_root = Path(__file__).resolve().parents[1]
cleaned_path = project_root / "data" / "ola_cleaned.csv"
full_path = project_root / "data" / "ola_full.csv"

if cleaned_path.exists():
    DATA_PATH = cleaned_path
elif full_path.exists():
    DATA_PATH = full_path
else:
    st.error("Dataset not found. Please place 'ola_cleaned.csv' or 'ola_full.csv' in the data/ folder.")
    st.stop()

DATA_PATH_STR = str(DATA_PATH)

# ---------------- Load Data (with spinner) ----------------
with st.spinner(f"Loading data from {DATA_PATH.name} ..."):
    try:
        df = load_data_cached(DATA_PATH_STR)
    except Exception as e:
        st.error(f"Error loading data: {e}")
        try:
            with open(DATA_PATH_STR, "r", encoding="utf-8", errors="replace") as fh:
                preview = "".join(fh.readlines()[:80])
                st.code(preview)
        except Exception:
            pass
        st.stop()

# show loaded path in sidebar & caption
st.sidebar.markdown(f"**Loaded dataset:** `{DATA_PATH.name}`")
st.caption(f"Data source: {DATA_PATH.name}")

# ---------------- Sidebar Filters ----------------
st.sidebar.header("Filters")

if "Datetime" in df.columns and not df["Datetime"].dropna().empty:
    try:
        min_date = df["Datetime"].dropna().min().date()
        max_date = df["Datetime"].dropna().max().date()
    except Exception:
        min_date = pd.to_datetime("2020-01-01").date()
        max_date = pd.to_datetime("2025-12-31").date()
else:
    min_date = pd.to_datetime("2020-01-01").date()
    max_date = pd.to_datetime("2025-12-31").date()

date_range = st.sidebar.date_input("Date range", [min_date, max_date])

vehicle_options = list(df["Vehicle_Type"].dropna().unique()) if "Vehicle_Type" in df.columns else []
payment_options = list(df["Payment_Method"].dropna().unique()) if "Payment_Method" in df.columns else []

vehicle_types = st.sidebar.multiselect("Vehicle type", options=vehicle_options, default=vehicle_options[:5] if vehicle_options else [])
payment_methods = st.sidebar.multiselect("Payment method", options=payment_options, default=payment_options if payment_options else [])

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

# ---------------- KPI cards (with colored backgrounds) ----------------
def kpi_card(label: str, value: str, bg: str = "#ffffff", color: str = "white"):
    html = f"""
    <div style="
        background: {bg};
        padding: 12px 16px;
        border-radius: 12px;
        box-shadow: rgba(0,0,0,0.06) 0px 4px 10px;
        text-align: left;
        color: {color};
        ">
        <div style="font-size:13px; opacity:0.9;">{label}</div>
        <div style="font-size:22px; font-weight:700; margin-top:6px;">{value}</div>
    </div>
    """
    return html


st.title("Ola Ride Insights Dashboard")
st.caption(f"Data source: {DATA_PATH.name}")

col1, col2, col3, col4, col5 = st.columns([1,1,1,1,1])

total_rides = f"{len(df_f):,}"
successful = int(((df_f["Booking_Status"] == "Success") if "Booking_Status" in df_f.columns else pd.Series(False, index=df_f.index)).sum())
canceled = int(((df_f["Booking_Status"] != "Success") if "Booking_Status" in df_f.columns else pd.Series(False, index=df_f.index)).sum())
cancellation_rate = f"{(canceled/len(df_f)*100):.2f}%" if len(df_f)>0 else "N/A"
total_revenue = f"₹{df_f['Booking_Value'].sum():,.2f}" if "Booking_Value" in df_f.columns else "N/A"
avg_rating = f"{df_f['Driver_Ratings'].mean():.2f}" if "Driver_Ratings" in df_f.columns else "N/A"

col1.markdown(kpi_card("Total Rides", total_rides, bg="#198754", color="#fff"), unsafe_allow_html=True)
col2.markdown(kpi_card("Successful Rides", f"{successful:,}", bg="#0d6efd", color="#fff"), unsafe_allow_html=True)
col3.markdown(kpi_card("Cancellation Rate", cancellation_rate, bg="#dc3545", color="#fff"), unsafe_allow_html=True)
col4.markdown(kpi_card("Total Booking Value", total_revenue, bg="#ff9100", color="#fff"), unsafe_allow_html=True)
col5.markdown(kpi_card("Avg Driver Rating", avg_rating, bg="#6f42c1", color="#fff"), unsafe_allow_html=True)

# ---------------- Utility actions: preview & download ----------------
st.markdown("### Dataset preview & export")
st.write(f"Filtered rows: **{len(df_f):,}**  |  Columns: **{len(df_f.columns):,}**")

with st.expander("Show sample rows"):
    st.dataframe(df_f.head(10))

csv_bytes = df_f.to_csv(index=False).encode("utf-8")
st.download_button("Download filtered data as CSV", data=csv_bytes, file_name="ola_filtered.csv", mime="text/csv")

# ---------------- SQL runner (in-memory SQLite) ----------------
conn = sqlite3.connect(":memory:")
try:
    df.to_sql("ola_rides", conn, index=False, if_exists="replace")
except Exception:
    safe_df = df.copy()
    safe_df.columns = [str(c).replace("-", "_").replace(" ", "_") for c in safe_df.columns]
    safe_df.to_sql("ola_rides", conn, index=False, if_exists="replace")

st.header("Run SQL (SQLite)")
default_sql = "SELECT Booking_ID, Date, Time, Booking_Status, Customer_ID, Vehicle_Type, Booking_Value, Payment_Method FROM ola_rides WHERE Booking_Status = 'Success' LIMIT 100;"
sql = st.text_area("SQL", value=default_sql, height=160)

if st.button("Run SQL"):
    try:
        res = pd.read_sql_query(sql, conn)
        st.dataframe(res)
    except Exception as e:
        st.error(f"SQL error: {e}")

# ---------------- Visualizations ----------------
st.header("Sample Visualizations")

st.subheader("📈 Ride Volume Over Time")
if "Datetime" in df_f.columns and not df_f["Datetime"].dropna().empty:
    rides_by_date = df_f.groupby(df_f["Datetime"].dt.date).size().rename("count")
    rides_by_date.index = pd.to_datetime(rides_by_date.index)
    st.line_chart(rides_by_date)
else:
    st.info("No valid Datetime column available for time series.")

st.subheader("💰 Revenue by Payment Method")
if "Payment_Method" in df_f.columns and "Booking_Value" in df_f.columns:
    rev_by_payment = df_f.groupby("Payment_Method")["Booking_Value"].sum().sort_values(ascending=False)
    st.bar_chart(rev_by_payment)
else:
    st.write("Payment_Method or Booking_Value column missing.")

st.subheader("🚗 Average Ride Distance by Vehicle Type")
if "Vehicle_Type" in df_f.columns and "Ride_Distance" in df_f.columns:
    avg_dist = df_f.groupby("Vehicle_Type")["Ride_Distance"].mean().sort_values(ascending=False)
    st.bar_chart(avg_dist)
else:
    st.write("Vehicle_Type or Ride_Distance column missing.")

st.subheader("👥 Top 10 Customers by Booking Value")
if "Customer_ID" in df_f.columns and "Booking_Value" in df_f.columns:
    top_customers = df_f.groupby("Customer_ID")["Booking_Value"].sum().nlargest(10).reset_index()
    st.table(top_customers)
else:
    st.write("Customer_ID or Booking_Value column missing.")

# ---------------- Power BI (offline-safe) — screenshot loop ----------------
st.header("Power BI Dashboard (Screenshots)")
fig_dir = project_root / "docs" / "figures"
imgs = sorted(fig_dir.glob("powerbi_*.png"))
if imgs:
    for i, img in enumerate(imgs):
        st.image(str(img), caption=f"Power BI page {i+1}: {img.name}", use_column_width=True)
else:
    st.info("No Power BI screenshots found in docs/figures (powerbi_*.png). You can export images from Power BI and save them there.")

# ---------------- About / Instructions ----------------
with st.expander("About / Instructions"):
    st.markdown(
        """
        **Ola Ride Insights — Streamlit App**

        **What this app does**
        - Loads the cleaned dataset (`data/ola_cleaned.csv`) when available, otherwise falls back to `data/ola_full.csv`.
        - Offers sidebar filters for date range, vehicle type and payment method.
        - Shows KPIs, time-series and summary charts.
        - Provides an in-memory SQL runner for quick queries.
        - Allows download of filtered data and includes Power BI screenshots.

        **How to run locally**
        1. Activate your virtual environment:
           - PowerShell: `.\.venv\Scripts\Activate.ps1` (or activate your venv).
        2. Install dependencies:
           - `pip install -r app/requirements.txt`
        3. Start the app:
           - `cd app`
           - `streamlit run streamlit_app.py`

        **Files to include in the repo**
        - `data/ola_cleaned.csv` (cleaned dataset)  [optional to include]
        - `docs/EDA.ipynb`, `docs/EDA.md`, `docs/EXECUTIVE_SUMMARY.md`
        - `docs/figures/*` (plots & screenshots, including `powerbi_*.png`)
        - `sql/queries.sql` (SQL answers)
        - `app/streamlit_app.py`, `app/requirements.txt`

        **Contact / Notes**
        - Built for the Ola Ride Insights capstone. If the app cannot find a cleaned dataset, run the EDA notebook to create `ola_cleaned.csv`.
        """
    )

st.info("Tip: Use the filters then download the filtered CSV for quick export during demos.")
