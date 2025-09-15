# DATA_CLEANING.md

## Purpose
This document describes the column-by-column data cleaning and preprocessing steps applied to the Ola rides dataset.

## Files
- data/ola_sample.csv — small sample for development
- data/ola_full.csv — full dataset (may be stored externally if large)
- data/ola_cleaned.csv — final cleaned dataset produced by the EDA notebook

---

## Column-by-column cleaning rules

**Date**  
- Parse as datetime. Use pd.to_datetime(..., errors='coerce').  
- Combine with Time column (if present) to create Datetime.

**Time**  
- Normalize to HH:MM:SS. Use as part of Datetime.

**Booking_ID**  
- Keep as string / unique identifier. Remove leading/trailing spaces.

**Booking_Status**  
- Standardize variants (e.g., Canceled by Driver, Canceled by Customer, Driver Not Found, Success).  
- Map typos and case differences to canonical values using .str.strip().str.title() and a mapping dict if needed.

**Customer_ID**  
- Keep as string. Check duplicates and top customers.

**Vehicle_Type**  
- Normalize categories (e.g., Prime Sedan, Prime SUV, Prime Plus, Mini, Bike, Auto, eBike).  
- Use ehicle-icons.csv mapping for UI icons.

**Pickup_Location / Drop_Location**  
- Strip whitespace. Fill missing with Unknown. Optionally geocode later for spatial analysis.

**V_TAT / C_TAT** (Turn-around times)  
- Convert to numeric. Coerce non-numeric -> NaN. Create summary stats and outlier handling.

**Canceled_Rides_by_Customer / Canceled_Rides_by_Driver**  
- Standardize text, convert to boolean/count where appropriate. Create cancellation_flag.

**Incomplete_Rides / Incomplete_Rides_Reason**  
- Standardize reasons. Treat empty/null as No.

**Booking_Value**  
- Convert to numeric (loat). Remove currency symbols and commas. Coerce errors -> NaN.

**Payment_Method**  
- Normalize to Cash, UPI, Credit Card, etc. Fill missing as Unknown.

**Ride_Distance**  
- Convert to numeric. Check for zero/negative values and outliers.

**Driver_Ratings / Customer_Rating**  
- Convert to numeric; clamp to valid range (0–5). Replace impossible values with NaN.

**Vehicle Images**  
- Column contains bad placeholders (#NAME?) — drop this column unless valid URLs are provided.

---

## Missing values & basics
- Replace string "null" / "NULL" with NaN.  
- For categorical columns use illna('Unknown') for UI; for numeric, consider median imputation or leave as NaN depending on analysis.  
- Save cleaned dataset: data/ola_cleaned.csv.

---

## Save & tracking notes
- Do not commit extremely large CSVs (>100 MB) to GitHub. Keep ola_sample.csv in repo and store ola_full.csv in Google Drive / GitHub Release / S3 if large.
- If you need the full CSV in the repo, use **Git LFS**.

