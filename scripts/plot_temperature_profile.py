import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('data/processed/argo_profiles_merged.csv')

# Select data for one float by float_id
float_sample = df['float_id'].iloc[0]
sample_data = df[df['float_id'] == float_sample]

plt.figure(figsize=(6,8))
plt.plot(sample_data['temperature'], sample_data['pressure'], marker='o')
plt.gca().invert_yaxis()
plt.xlabel('Temperature (°C)')
plt.ylabel('Pressure (dbar)')
plt.title(f'Temperature Profile for Float ID: {float_sample}')
plt.grid(True)
plt.show()
