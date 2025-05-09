import pandas as pd
import random
import numpy as np
from datetime import datetime, timedelta

# Set random seed for reproducibility
random.seed(42)
np.random.seed(42)

# Generate 100 timestamps starting from a given time
start_time = datetime(2025, 5, 8, 8, 0)
timestamps = [start_time + timedelta(hours=i) for i in range(100)]

# Feedstock types
feedstock_types = ['HDPE', 'LDPE', 'PP', 'PS', 'Mixed (PP/PE)']

# Catalysts
catalysts = ['Zeolite ZSM-5', 'Al-SBA-15', 'Silica-Alumina', 'None']

# Create the data
data = {
    "ID": list(range(1, 101)),
    "Timestamp": timestamps,
    "Feedstock Type": [random.choice(feedstock_types) for _ in range(100)],
    "Feed Rate (kg/h)": np.random.uniform(45, 55, 100).round(2),
    "Reactor Temp (°C)": np.random.uniform(430, 470, 100).round(1),
    "Heating Rate (°C/min)": np.random.uniform(10, 20, 100).round(1),
    "Residence Time (min)": np.random.uniform(40, 60, 100).round(1),
    "Reactor Pressure (bar)": np.random.uniform(1.0, 1.5, 100).round(2),
    "Yield – Oil (wt%)": np.random.uniform(60, 70, 100).round(1),
    "Yield – Gas (wt%)": np.random.uniform(20, 30, 100).round(1),
    "Yield – Char (wt%)": np.random.uniform(5, 12, 100).round(1),
    "Energy Input (kWh)": np.random.uniform(110, 130, 100).round(1),
    "Oil Calorific Value (MJ/kg)": np.random.uniform(40, 43, 100).round(2),
    "Gas Composition (C1–C5 wt%)": np.random.uniform(85, 90, 100).round(1),
    "Catalyst Used": [random.choice(catalysts) for _ in range(100)],
    "Catalyst Loading (wt%)": np.random.uniform(0, 6, 100).round(1),
    "Condenser Temp (°C)": np.random.uniform(20, 30, 100).round(1),
    "Oil Viscosity (cP)": np.random.uniform(2.0, 3.0, 100).round(2),
    "pH of Oil": np.random.uniform(6.5, 7.5, 100).round(2),
    "Gas Flow Rate (Nm³/h)": np.random.uniform(17, 20, 100).round(2)
}

# Create DataFrame
df = pd.DataFrame(data)

# Save to Excel file
excel_path = "../data/plastic_pyrolysis_data_table.xlsx"
df.to_excel(excel_path, index=False)

excel_path