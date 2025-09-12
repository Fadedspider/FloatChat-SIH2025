import pandas as pd

df = pd.read_csv("dashboard_11-09-2025_10-51-53.csv", sep=";")
on_bad_lines="skip"   # skip problematic rows


wmo_list = df["WMO"].tolist()
print(wmo_list)
