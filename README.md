🚖 Ola Ride Insights

End-to-end mini-capstone project analyzing Ola ride data to produce actionable business insights.
Includes: SQL query templates, data cleaning & EDA, Power BI dashboards, and a Streamlit app that presents insights interactively.

Recommended repo tags: data-science, streamlit, powerbi, sql, eda, data-cleaning, visualization, ride-sharing, ola

🔎 Project Overview

This project explores Ola ride-sharing data to identify demand patterns, cancellation causes, driver/customer ratings, and revenue drivers.

Deliverables include:

✅ Cleaned dataset and EDA

✅ SQL query templates for common business questions

✅ Interactive Power BI report (Overall, Vehicle Type, Revenue, Cancellation, Ratings views)

✅ Streamlit app that runs SQL, shows KPIs/visualizations, and embeds Power BI insights

📁 Repository Structure
ola-ride-insights/
├─ data/
│   ├─ ola_cleaned_with_cancellations.csv   # main cleaned dataset
│   ├─ ola_sample.csv                       # optional sample dataset
│   ├─ ola_full.csv                         # full dataset
│   ├─ ola_cleaned.csv                      # cleaned base dataset
├─ sql/
│   ├─ queries.sql                          # SQL templates for analysis
├─ docs/
│   ├─ figures/                             # Power BI PDF + exported figures
│   ├─ DATA_CLEANING.md
│   ├─ EDA.md
├─ app/
│   ├─ streamlit_app.py                     # Streamlit app (main)
│   ├─ requirements.txt
├─ ola_ride_insights.pbix                   # (optional, not tracked in GitHub if >100MB)
├─ README.md

🧾 Dataset

Primary CSV: data/ola_cleaned_with_cancellations.csv (≈103,025 rows, 26 columns).

Contains booking status, cancellations, customer/driver ratings, revenue, and ride details.

For larger datasets, use cloud storage (Google Drive, OneDrive, Releases).

📊 Power BI Report

The full Power BI dashboard is available as a PDF:
👉 📂 Download ola_ride_insights.pdf

If you need the .pbix file, please contact the author (not committed due to size limits).

🚀 Streamlit App

👉 Live App: Ola Ride Insights Streamlit App

Run locally:

# Clone repo
git clone https://github.com/<your-username>/ola-ride-insights.git
cd ola-ride-insights/app

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate   # Windows
source .venv/bin/activate   # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run streamlit_app.py

🧭 Power BI Notes

Built in Power BI Desktop → published as .pbix → exported as .pdf.

Interactive dashboard contains:

Overall KPIs (revenue, rides, cancellations)

Vehicle Type analysis

Revenue insights

Cancellation breakdowns

Ratings distribution

🧹 Data Cleaning

Key steps:

Combine Date + Time → single Datetime column.

Normalize Booking_Status (Success, Canceled by Driver, Canceled by Customer, Driver Not Found).

Convert numeric fields (Booking_Value, Ride_Distance, Driver_Ratings, Customer_Rating) → numeric types.

Replace nulls with NaN or Unknown.

Drop irrelevant columns.

Details in docs/DATA_CLEANING.md
.

🧪 Testing & Validation

SQL queries in sql/queries.sql validated against Pandas aggregations.

Cross-checks:

Total rides = Sum of statuses

Cancellation counts consistent across SQL and Power BI

📜 License & Contact

License: MIT

Author: Shruti S Ghosh

Contact: 📩 shrutisghosh@outlook.com
