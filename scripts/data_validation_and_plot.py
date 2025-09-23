# Filename: data_validation_and_plot.py

import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('data/processed/argo_profiles_merged.csv')
print(df.info())
print(df.describe())

# Example: Temperature profile for one float ID
sample = df[df['float_id'] == df['float_id'].iloc[0]]  # Select first float's data
plt.plot(sample['temperature'], sample['pressure'])
plt.gca().invert_yaxis()
plt.xlabel('Temperature [°C]')
plt.ylabel('Pressure [dbar]')
plt.title(f"Temperature Profile for float {sample['float_id'].iloc[0]}")
plt.show()