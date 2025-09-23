import pandas as pd

def preprocess_argo_csv(input_path, output_path):
    # Load CSV file
    df = pd.read_csv(input_path)

    # Drop rows with missing lat, lon, or time values
    df = df.dropna(subset=['lat', 'lon', 'time'])

    # Convert quality control columns to integers after filling missing as 0
    df['temp_qc'] = df['temp_qc'].fillna(0).astype(int)
    df['salinity_qc'] = df['salinity_qc'].fillna(0).astype(int)

    # Create 'geom' column as WKT POINT(longitude latitude) for reference
    df['geom'] = df.apply(lambda row: f'POINT({row.lon} {row.lat})', axis=1)

    # Drop 'geom' column before saving CSV for PostgreSQL import
    df = df.drop(columns=['geom'])

    # Save the cleaned CSV file without 'geom' column
    df.to_csv(output_path, index=False)
    print(f"Cleaned CSV saved to {output_path} without 'geom' column for PostgreSQL import.")

# File paths
input_csv = r'data\processed\argo_profiles_merged.csv'
output_csv = r'data\processed\argo_profiles_final_cleaned.csv'

# Run preprocessing
preprocess_argo_csv(input_csv, output_csv)
