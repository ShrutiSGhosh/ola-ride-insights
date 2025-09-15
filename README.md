# ola-ride-insights
Ola Ride Insights — end-to-end ride-sharing analytics: SQL + Power BI dashboards + Streamlit app for interactive BI and business insights.  Recommended repo topics/tags: data-science, streamlit, powerbi, sql, eda, data-cleaning, visualization, ride-sharing, ola
# Ola Ride Insights

**End-to-end mini-capstone project** analyzing Ola ride data to produce business insights.  
Includes: SQL query templates, data cleaning & EDA, Power BI dashboards, and a Streamlit app that presents insights interactively.

---

## 🔎 Project Overview
This project explores Ola ride-sharing data to identify demand patterns, cancellation causes, driver/customer ratings, and revenue drivers. Deliverables include:
- Cleaned dataset and EDA
- SQL query templates for common business questions
- Interactive Power BI report (Overall, Vehicle Type, Revenue, Cancellation, Ratings views)
- Streamlit app that runs SQL, shows KPIs/visualizations and embeds Power BI visuals

---

## 📁 Repository structure
ola-ride-insights/
├─ data/
│ ├─ ola_sample.csv # sample or full dataset (if permitted)
│ ├─ summary_sheet.csv # aggregated sheet(s) (vehicle averages etc.)
│ ├─ vehicle-icons.csv # vehicle type → icon URL mapping
├─ sql/
│ ├─ queries.sql # SQL templates for requested queries
├─ powerbi/
│ ├─ notes.md # Power BI build & embed instructions
├─ app/
│ ├─ streamlit_app.py # Streamlit app (main)
│ ├─ requirements.txt
├─ docs/
│ ├─ DATA_CLEANING.md
│ ├─ EDA.md
├─ .gitignore
├─ README.md


---

## 🧾 Dataset
- Primary CSV: `data/ola_sample.csv` (≈103,025 rows, 20 columns).  
- Aggregates / other sheets: include `data/summary_sheet.csv` (e.g. avg distances per vehicle, booking status counts).
- If file size is large, store dataset in a release, Google Drive, or cloud storage; add download instructions in `DATA_CLEANING.md`.

---

## 🚀 How to run locally
1. Clone the repo:
```bash
git clone https://github.com/<ShrutiSGhosh>/ola-ride-insights.git
cd ola-ride-insights/app
Create a virtual environment and install dependencies:

python -m venv .venv
source .venv/bin/activate   # mac/linux
.venv\Scripts\activate      # windows
pip install -r requirements.txt


Start the Streamlit app:

streamlit run streamlit_app.py


The app by default loads data/ola_sample.csv. If you store the CSV elsewhere (raw GitHub URL or cloud), update RAW_GITHUB_URL inside the app.

☁️ Deploy on Streamlit Community Cloud

Push your repo to GitHub.

Sign in to https://streamlit.io/cloud
 with GitHub.

Create a new app → select repo/branch and set app/streamlit_app.py as the main file.

Add secrets (if any) under app settings (Power BI embed tokens, DB creds).

Deploy.

🧭 Power BI & Embed notes

Build reports in Power BI Desktop, publish to Power BI Service.

Embed to Streamlit using an iframe (public publish to web) or secure embed token (Power BI Embedded/Azure).

See powerbi/notes.md for step-by-step embed options and security considerations.

📌 Vehicle icons mapping (useful for UI)

Add data/vehicle-icons.csv with Vehicle_Type,Icon_URL. Example:

Prime Sedan,https://cdn-icons-png.flaticon.com/128/14183/14183770.png
Bike,https://cdn-icons-png.flaticon.com/128/9983/9983173.png
Prime SUV,https://cdn-icons-png.flaticon.com/128/9983/9983204.png
eBike,https://cdn-icons-png.flaticon.com/128/6839/6839867.png
Mini,https://cdn-icons-png.flaticon.com/128/3202/3202926.png
Prime Plus,https://cdn-icons-png.flaticon.com/128/11409/11409716.png
Auto,https://cdn-icons-png.flaticon.com/128/16526/16526595.png


In Streamlit you can fetch the URL and show st.image(icon_url, width=48) next to a vehicle label.

🧹 Data cleaning notes

Convert Date + Time → a single datetime column.

Normalize Booking_Status (e.g., Canceled by Driver, Canceled by Customer, Driver Not Found, Success).

Convert numeric columns (Booking_Value, Ride_Distance, Driver_Ratings, Customer_Rating, V_TAT, C_TAT) to numeric, coerce errors → NaN.

Replace null strings with actual NaN or Unknown for categorical fields.

Drop Vehicle Images column if not usable.

(See docs/DATA_CLEANING.md for the column-by-column plan.)

🧪 Testing & validation

Keep sql/queries.sql and validate each SQL result by cross-checking with Pandas aggregation in notebooks.

Add unit checks (small scripts) for counts like total rides == sum of statuses.

🤝 Contributing

Use main for releases & dev for active development. Create feature branches: feature/streamlit-filters, feature/powerbi-report.

Pull Request template: title, short description, related files changed, test checklist.

📜 License & Contact

License: MIT 

Contact: <shrutisghosh@outlook.com>
