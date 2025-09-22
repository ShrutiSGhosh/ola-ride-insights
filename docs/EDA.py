# docs/EDA.py
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

sample_path = "../data/ola_sample.csv"
full_path = "../data/ola_full.csv"

try:
    df = pd.read_csv(full_path, parse_dates=["Date"], infer_datetime_format=True)
    print("Loaded FULL dataset")
except FileNotFoundError:
    df = pd.read_csv(sample_path, parse_dates=["Date"], infer_datetime_format=True)
    print("Loaded SAMPLE dataset")

print("Shape:", df.shape)
print(df.columns.tolist())

# Basic cleaning
df.columns = [c.strip() for c in df.columns]
df['Booking_Status'] = df['Booking_Status'].astype(str).str.strip().str.title()
num_cols = ['Booking_Value','Ride_Distance','Driver_Ratings','Customer_Rating','V_TAT','C_TAT']
for col in num_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')

if 'Time' in df.columns:
    df['Datetime'] = pd.to_datetime(df['Date'].astype(str) + ' ' + df['Time'].astype(str), errors='coerce')
else:
    df['Datetime'] = pd.to_datetime(df['Date'], errors='coerce')

# Quick checks
print("\nBooking status distribution:\n", df['Booking_Status'].value_counts(dropna=False).head())
if 'Payment_Method' in df.columns:
    print("\nPayment method distribution:\n", df['Payment_Method'].value_counts().head())
if 'Vehicle_Type' in df.columns:
    print("\nTop vehicle types:\n", df['Vehicle_Type'].value_counts().head())

# Save cleaned csv
df.to_csv("../data/ola_cleaned.csv", index=False)
print("\nSaved cleaned data to ../data/ola_cleaned.csv")

