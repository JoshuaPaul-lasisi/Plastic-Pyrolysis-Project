# Imports
import pandas as pd
import random
import numpy as np
from datetime import datetime, timedelta

# First, we need to define or load the input DataFrame 'df'
# Since it's not provided in the original code, I'll create a sample one
data = {
    "Feedstock Type": ["HDPE", "LDPE", "PP", "PS", "Mixed (PP/PE)"],
    "Reactor Temp (°C)": [450, 440, 460, 430, 455],
    "Heating Rate (°C/min)": [10, 15, 12, 8, 10],
    "Residence Time (min)": [30, 45, 35, 40, 38],
    "Catalyst Used": ["Zeolite", "None", "Alumina", "None", "Zeolite"],
    "Energy Input (kWh)": [25, 30, 28, 22, 27],
    "Yield – Oil (wt%)": [75, 70, 72, 68, 73],
    "Yield – Gas (wt%)": [15, 20, 18, 22, 17],
    "Yield – Char (wt%)": [10, 10, 10, 10, 10],
    "Oil Calorific Value (MJ/kg)": [42, 40, 41, 39, 41.5]
}
df = pd.DataFrame(data)

# 1. plastic_feedstock table
plastic_types = {
    "HDPE": ("High-Density Polyethylene", 0.95, 130, 470, "none"),
    "LDPE": ("Low-Density Polyethylene", 0.92, 110, 450, "dyes"),
    "PP": ("Polypropylene", 0.90, 160, 480, "fillers"),
    "PS": ("Polystyrene", 1.05, 100, 460, "none"),
    "Mixed (PP/PE)": ("Mixed Polypropylene and Polyethylene", 0.93, 135, 475, "mixed")
}
plastic_feedstock = pd.DataFrame([
    {
        "plastic_id": pid,
        "plastic_type": vals[0],
        "density": vals[1],
        "melting_point": vals[2],
        "degradation_temp": vals[3],
        "additives_present": vals[4]
    }
    for pid, vals in plastic_types.items()
])

# 2. blend_compositions table
blend_ids = [f"B{i+1}" for i in range(len(df))]
blend_compositions = []
for idx, row in df.iterrows():
    blend_id = blend_ids[idx]
    feedstock = row["Feedstock Type"]
    if "Mixed" in feedstock:
        for sub in ["PP", "HDPE"]:
            blend_compositions.append({
                "blend_id": blend_id,
                "plastic_id": sub,
                "percentage": 50.0
            })
    else:
        blend_compositions.append({
            "blend_id": blend_id,
            "plastic_id": feedstock,
            "percentage": 100.0
        })
blend_compositions = pd.DataFrame(blend_compositions)

# 3. pyrolysis_conditions table
pyrolysis_conditions = pd.DataFrame({
    "condition_id": [f"C{i+1}" for i in range(len(df))],
    "blend_id": blend_ids,
    "temperature": df["Reactor Temp (°C)"],
    "heating_rate": df["Heating Rate (°C/min)"],
    "residence_time": df["Residence Time (min)"],
    "catalyst": df["Catalyst Used"],
    "reactor_type": ["batch"] * len(df),
    "energy_input": df["Energy Input (kWh)"]
})

# 4. pyrolysis_outputs table
pyrolysis_outputs = pd.DataFrame({
    "output_id": [f"O{i+1}" for i in range(len(df))],
    "condition_id": pyrolysis_conditions["condition_id"],
    "fuel_yield": df["Yield – Oil (wt%)"],
    "gas_yield": df["Yield – Gas (wt%)"],
    "char_yield": df["Yield – Char (wt%)"],
    "fuel_energy_content": df["Oil Calorific Value (MJ/kg)"],
    "emissions": np.random.uniform(1.0, 2.5, len(df)).round(2),
    "efficiency": (df["Oil Calorific Value (MJ/kg)"] * df["Yield – Oil (wt%)"] / df["Energy Input (kWh)"]).round(3)
})

# Save all tables to CSV files
plastic_feedstock_path = "../data/plastic_feedstock.csv"
blend_compositions_path = "../data/blend_compositions.csv"
pyrolysis_conditions_path = "../data/pyrolysis_conditions.csv"
pyrolysis_outputs_path = "../data/pyrolysis_outputs.csv"

plastic_feedstock.to_csv(plastic_feedstock_path, index=False)
blend_compositions.to_csv(blend_compositions_path, index=False)
pyrolysis_conditions.to_csv(pyrolysis_conditions_path, index=False)
pyrolysis_outputs.to_csv(pyrolysis_outputs_path, index=False)

plastic_feedstock_path, blend_compositions_path, pyrolysis_conditions_path, pyrolysis_outputs_path