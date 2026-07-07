# Automated Test Log Analyzer & Outlier Dashboard

A Python tool that parses multi-channel sensor log data, flags anomalous 
readings using rolling statistical thresholds, and visualizes results in 
an interactive dashboard.

## Dataset
UCI Air Quality dataset — hourly readings from 5 metal-oxide gas sensors 
plus temperature and humidity, collected over roughly one year in an 
Italian city. Chosen as a stand-in for real-world multi-channel sensor 
log data with realistic noise and missing values.

## How it works
- Missing readings (marked as -200 in the raw data) are cleaned and 
  converted to proper NaN values.
- For each sensor, a rolling 24-hour mean and standard deviation are 
  computed.
- Each reading's z-score relative to its own rolling window is calculated.
- Readings with |z-score| > 3 are flagged as anomalies (this threshold 
  is configurable).
- Results are summarized in a per-sensor anomaly report and visualized 
  in an interactive Plotly dashboard.

## Running it

```bash
pip install -r requirements.txt
python analyzer.py
python dashboard.py
```

Open `dashboard.html` in a browser to view the interactive dashboard.

## Limitations

- Uses a fixed z-score threshold rather than an adaptive one; this assumes each rolling window is roughly normally distributed, which may not hold during rapid genuine trend changes (e.g. actual pollution spikes).
- The 24-hour window size was chosen for this hourly dataset and would need to be re-tuned for data at a different sampling rate.