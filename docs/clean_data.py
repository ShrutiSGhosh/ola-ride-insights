"""
Data cleaning for Ola Ride Insights.
Reads ola_full.csv (raw) or ola_sample.csv, cleans, and writes ola_cleaned.csv.
"""

import pandas as pd
import numpy as np
import os

RAW_FULL = os.path.join("..", "data", "ola_full.csv")
RAW_SAMPLE = os.path.join("..", "data", "ola_sample.csv")
CLEANED = os.path.join("..", "data", "ola_cleaned.csv")

def clean_ola(path_in, path_out):
    # Load CSV (allow bad lines but keep structure)
    df = pd.read_csv(path_in, engine="python", on_bad_lines="skip")
    df.columns = [c.strip().replace("\ufeff", "").rstrip(",") for c in df.columns]

    # Drop trailing empty col if present
    if df.columns[-1] == "" or df.columns[-1].lower().startswith("unnamed"):
        df = df.iloc[:, :-1]

    # Replace textual nulls
    df = df.replace({"null": np.nan, "NULL": np.nan, "NaN": np.nan, "": np.nan})

    # Create Datetime from Date + Time if both exist
    if "Date" in df.columns and "Time" in df.columns:
        df["Datetime"] = pd.to_datetime(df["Date"].astype(str).str.strip() + " " +
                                        df["Time"].astype(str).str.strip(),
                                        errors="coerce")
    elif "Date" in df.columns:
        df["Datetime"] = pd.to_datetime(df["Date"], errors="coerce")

    # Convert numerics
    for col in ["Booking_Value", "Ride_Distance", "Driver_Ratings", "Customer_Rating", "V_TAT", "C_TAT"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Normalize Booking_Status
    if "Booking_Status" in df.columns:
        df["Booking_Status"] = df["Booking_Status"].astype(str).str.strip().str.title()

    # Trim string cols
    for col in ["Customer_ID", "Booking_ID", "Vehicle_Type", "Payment_Method", "Pickup_Location", "Drop_Location"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().replace({"nan": np.nan})

    df.to_csv(path_out, index=False)
    print(f"Cleaned file saved: {path_out}, rows={len(df)}")

if __name__ == "__main__":
    if os.path.exists(RAW_FULL):
        clean_ola(RAW_FULL, CLEANED)
    elif os.path.exists(RAW_SAMPLE):
        clean_ola(RAW_SAMPLE, CLEANED)
    else:
        print("No raw dataset found.")
