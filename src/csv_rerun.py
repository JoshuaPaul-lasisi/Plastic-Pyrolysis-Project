# Re-run generation after code execution state reset
import pandas as pd
import numpy as np
import random

# Set random seed for reproducibility
np.random.seed(42)
random.seed(42)

# Constants
N_ROWS = 1000  # Number of experiments
plastic_ids = ["HDPE", "LDPE", "PP", "PS"]
catalysts = ["Zeolite", "Alumina", "Silica", np.nan]

# Generate plastic_feedstock table (unchanged, 4 entries)
plastic_feedstock = pd.DataFrame([
    {"plastic_id": "HDPE", "plastic_type": "High-Density Polyethylene", "density": 0.95, "melting_point": 130, "degradation_temp": 470, "additives_present": "none"},
    {"plastic_id": "LDPE", "plastic_type": "Low-Density Polyethylene", "density": 0.92, "melting_point": 110, "degradation_temp": 450, "additives_present": "dyes"},
    {"plastic_id": "PP", "plastic_type": "Polypropylene", "density": 0.90, "melting_point": 160, "degradation_temp": 480, "additives_present": "fillers"},
    {"plastic_id": "PS", "plastic_type": "Polystyrene", "density": 1.05, "melting_point": 100, "degradation_temp": 460, "additives_present": "none"}
])

# Generate blend_compositions
blend_ids = [f"B{i+1}" for i in range(N_ROWS)]
blend_rows = []
for blend_id in blend_ids:
    plastics = np.random.choice(plastic_ids, size=random.randint(1, 3), replace=False)
    percentages = np.random.dirichlet(np.ones(len(plastics)), size=1)[0] * 100
    for p, perc in zip(plastics, percentages):
        blend_rows.append({"blend_id": blend_id, "plastic_id": p, "percentage": round(perc, 2)})
blend_compositions = pd.DataFrame(blend_rows)

# Generate pyrolysis_conditions
condition_ids = [f"C{i+1}" for i in range(N_ROWS)]
pyrolysis_conditions = pd.DataFrame({
    "condition_id": condition_ids,
    "blend_id": blend_ids,
    "temperature": np.random.randint(420, 480, N_ROWS),
    "heating_rate": np.random.uniform(8, 20, N_ROWS).round(1),
    "residence_time": np.random.randint(30, 60, N_ROWS),
    "catalyst": np.random.choice(catalysts, N_ROWS),
    "reactor_type": ["batch"] * N_ROWS,
    "energy_input": np.random.uniform(20, 40, N_ROWS).round(1)
})

# Generate pyrolysis_outputs
fuel_yield = np.random.uniform(60, 80, N_ROWS)
gas_yield = np.random.uniform(15, 30, N_ROWS)
char_yield = 100 - (fuel_yield + gas_yield)
fuel_energy_content = np.random.uniform(38, 43, N_ROWS).round(1)
emissions = np.random.uniform(1.0, 2.5, N_ROWS).round(2)
efficiency = (fuel_energy_content * fuel_yield / pyrolysis_conditions["energy_input"]).round(3)

pyrolysis_outputs = pd.DataFrame({
    "output_id": [f"O{i+1}" for i in range(N_ROWS)],
    "condition_id": condition_ids,
    "fuel_yield": fuel_yield.round(1),
    "gas_yield": gas_yield.round(1),
    "char_yield": char_yield.round(1),
    "fuel_energy_content": fuel_energy_content,
    "emissions": emissions,
    "efficiency": efficiency
})

# Save files
plastic_feedstock.to_csv("../data/plastic_feedstock.csv", index=False)
blend_compositions.to_csv("../data/blend_compositions.csv", index=False)
pyrolysis_conditions.to_csv("../data/pyrolysis_conditions.csv", index=False)
pyrolysis_outputs.to_csv("../data/pyrolysis_outputs.csv", index=False)

[
    "../data/plastic_feedstock.csv",
    "../data/blend_compositions.csv",
    "../data/pyrolysis_conditions.csv",
    "../data/pyrolysis_outputs.csv"
]
