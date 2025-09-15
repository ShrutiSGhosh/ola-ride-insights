# app/streamlit_app.py
import streamlit as st
import pandas as pd
import sqlite3

st.set_page_config(page_title="Ola Ride Insights", layout="wide")

@st.cache_data
def load_data(csv_path: str):
    df = pd.read_csv(csv_path, parse_dates=["Date"], dayfirst=False, infer_datetime_format=True)
    df.columns = [c.strip() for c in df.columns]

    # normalize booking status
    df['Booking_Status'] = df['Booking_Status'].astype(str).str.strip().str.title()

    # convert numeric fields
    for col in ['Booking_Value','Ride_Distance','Driver_Ratings','Customer_Rating','V_TAT','C_TAT']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # combine Date + Time if Time exists
    if 'Time' in df.columns:
        try:
            df['Datetime'] = pd.to_datetime(df['Date'].astype(str) + ' ' + df['Time'].astype(str), errors='coerce')
        except Exception:
            df['Datetime'] = pd.to_datetime(df['Date'], errors='coerce')
    else:
        df['Datetime'] = pd.to_datetime(df['Date'], errors='coerce')

    return df

# ---------------- Sidebar ----------------
st.sidebar.header("Dataset Selection")
DATA_SOURCE = st.sidebar.radio(
    "Select dataset:", 
    ["Sample (small)", "Full (large)"]
)

if DATA_SOURCE == "Sample (small)":
    DATA_PATH = "../data/ola_sample.csv"
else:
    DATA_PATH = "../data/ola_full.csv"   # make sure you add this file

try:
    df = load_data(DATA_PATH)
except FileNotFoundError:
    st.error(f"Could not find {DATA_PATH}. Please upload the CSV to /data folder.")
    st.stop()

# ---------------- Filters ----------------
st.sidebar.header("Filters")
min_date = df['Datetime'].min().date()
max_date = df['Datetime'].max().date()

date_range = st.sidebar.date_input("Date range", [min_date, max_date])
vehicle_types = st.sidebar.multiselect("Vehicle type", options=df['Vehicle_Type'].dropna().unique(), default=list(df['Vehicle_Type'].dropna().unique())[:5])
payment_methods = st.sidebar.multiselect("Payment method", options=df['Payment_Method'].dropna().unique(), default=list(df['Payment_Method'].dropna().unique()))

mask = (df['Datetime'].dt.date >= date_range[0]) & (df['Datetime'].dt.date <= date_range[1])
if vehicle_types:
    mask &= df['Vehicle_Type'].isin(vehicle_types)
if payment_methods:
    mask &= df['Payment_Method'].isin(payment_methods)

df_f = df.loc[mask].copy()

# ---------------- KPIs ----------------
st.title("Ola Ride Insights Dashboard")
col1,col2,col3,col4 = st.columns(4)
col1.metric("Total Rides", len(df_f))
col2.metric("Successful Rides", int((df_f['Booking_Status']=='Success').sum()))
col3.metric("Total Booking Value", f"{df_f['Booking_Value'].sum():.2f}")
col4.metric("Avg Driver Rating", f"{df_f['Driver_Ratings'].mean():.2f}")

# ---------------- SQL Queries ----------------
conn = sqlite3.connect(":memory:")
df.to_sql("ola_rides", conn, index=False, if_exists="replace")

st.header("Run SQL (SQLite)")
default_sql = "SELECT Booking_ID, Date, Time, Booking_Status, Customer_ID, Vehicle_Type, Booking_Value, Payment_Method FROM ola_rides WHERE Booking_Status = 'Success' LIMIT 100;"
sql = st.text_area("SQL", value=default_sql, height=180)

if st.button("Run SQL"):
    try:
        res = pd.read_sql_query(sql, conn)
        st.dataframe(res)
    except Exception as e:
        st.error(f"SQL error: {e}")

# ---------------- Visualizations ----------------
st.header("Sample Visualizations")

st.subheader("📈 Ride Volume Over Time")
rides_by_date = df_f.groupby(df_f['Datetime'].dt.date).size().rename("count").reset_index()
st.line_chart(rides_by_date.set_index('Datetime'))

st.subheader("💰 Revenue by Payment Method")
rev_by_payment = df_f.groupby('Payment_Method')['Booking_Value'].sum().reset_index().sort_values('Booking_Value', ascending=False)
st.bar_chart(rev_by_payment.set_index('Payment_Method'))

st.subheader("👥 Top 10 Customers by Booking Value")
top_customers = df_f.groupby('Customer_ID')['Booking_Value'].sum().nlargest(10).reset_index()
st.table(top_customers)

st.info("Switch dataset from the sidebar to test with sample data or full data.")
