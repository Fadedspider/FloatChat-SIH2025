import pandas as pd

# Load the two CSV files
df1 = pd.read_csv('data/processed/argo_profiles_cleaned.csv')
df2 = pd.read_csv('data/processed/argo_profiles_cleaned2.csv')

# Concatenate the dataframes vertically (stack rows)
merged_df = pd.concat([df1, df2], ignore_index=True)

# Optionally, drop duplicates if needed
# merged_df = merged_df.drop_duplicates()

# Save the merged dataframe to a new CSV file
merged_df.to_csv('data/processed/argo_profiles_merged.csv', index=False)

print('CSV files merged successfully and saved as argo_profiles_merged.csv')
