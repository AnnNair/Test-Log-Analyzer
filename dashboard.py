import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# --- Re-run the same processing from analyzer.py ---
df = pd.read_csv("data/AirQualityUCI.csv", sep=";", decimal=",")
df = df.dropna(how="all", axis=1)
df = df.dropna(how="all", axis=0)
df = df.replace(-200, pd.NA)

df["Datetime"] = pd.to_datetime(
    df["Date"] + " " + df["Time"].str.replace(".", ":", regex=False),
    format="%d/%m/%Y %H:%M:%S",
    errors="coerce"
)
df = df.dropna(subset=["Datetime"]).sort_values("Datetime")

sensor_cols = ["PT08.S1(CO)", "PT08.S2(NMHC)", "PT08.S3(NOx)",
               "PT08.S4(NO2)", "PT08.S5(O3)", "T", "RH"]

for col in sensor_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")

window = 24
for col in sensor_cols:
    df[f"{col}_roll_mean"] = df[col].rolling(window, min_periods=6).mean()
    df[f"{col}_roll_std"] = df[col].rolling(window, min_periods=6).std()
    df[f"{col}_zscore"] = (df[col] - df[f"{col}_roll_mean"]) / df[f"{col}_roll_std"]
    df[f"{col}_anomaly"] = df[f"{col}_zscore"].abs() > 3

# --- Build the dashboard ---
fig = make_subplots(rows=len(sensor_cols), cols=1, shared_xaxes=True,
                     subplot_titles=sensor_cols)

for i, col in enumerate(sensor_cols, start=1):
    fig.add_trace(go.Scatter(x=df["Datetime"], y=df[col], mode="lines",
                              name=col, line=dict(width=1)), row=i, col=1)

    anomalies = df[df[f"{col}_anomaly"]]
    fig.add_trace(go.Scatter(x=anomalies["Datetime"], y=anomalies[col],
                              mode="markers", name=f"{col} anomaly",
                              marker=dict(color="red", size=5)), row=i, col=1)

fig.update_layout(height=250 * len(sensor_cols), showlegend=False,
                   title="Sensor Trends with Flagged Anomalies")

fig.write_html("dashboard.html")
print("Dashboard saved to dashboard.html")