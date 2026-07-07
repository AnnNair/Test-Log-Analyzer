import pandas as pd

df = pd.read_csv("data/AirQualityUCI.csv", sep=";", decimal=",")
df = df.dropna(how="all", axis=1)  # drop empty columns
df = df.dropna(how="all", axis=0)  # drop empty rows

# UCI marks missing sensor readings as -200 - replace with NaN
df = df.replace(-200, pd.NA)

# Combine Date + Time into one datetime column
df["Datetime"] = pd.to_datetime(
    df["Date"] + " " + df["Time"].str.replace(".", ":", regex=False),
    format="%d/%m/%Y %H:%M:%S",
    errors="coerce"
)

df = df.dropna(subset=["Datetime"]).sort_values("Datetime")

print(df.shape)
print(df[["Datetime"]].head())
print(df["Datetime"].isna().sum(), "invalid datetimes remaining")
sensor_cols = ["PT08.S1(CO)", "PT08.S2(NMHC)", "PT08.S3(NOx)",
               "PT08.S4(NO2)", "PT08.S5(O3)", "T", "RH"]

for col in sensor_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")

print(df[sensor_cols].describe())
window = 24  # 24-hour rolling window

for col in sensor_cols:
    df[f"{col}_roll_mean"] = df[col].rolling(window, min_periods=6).mean()
    df[f"{col}_roll_std"] = df[col].rolling(window, min_periods=6).std()

    # z-score relative to rolling window
    df[f"{col}_zscore"] = (df[col] - df[f"{col}_roll_mean"]) / df[f"{col}_roll_std"]

    # flag anomaly if |z| exceeds threshold
    df[f"{col}_anomaly"] = df[f"{col}_zscore"].abs() > 3

# Quick check: how many anomalies flagged per sensor
for col in sensor_cols:
    n_anomalies = df[f"{col}_anomaly"].sum()
    print(f"{col}: {n_anomalies} anomalies flagged")
    summary = []
for col in sensor_cols:
    n_anomalies = df[f"{col}_anomaly"].sum()
    total = df[col].notna().sum()
    summary.append({
        "Sensor": col,
        "Total Readings": total,
        "Anomalies Flagged": int(n_anomalies),
        "Anomaly Rate (%)": round(100 * n_anomalies / total, 2) if total else 0
    })

summary_df = pd.DataFrame(summary)
print(summary_df)