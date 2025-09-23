import os
import xarray as xr
import pandas as pd
import numpy as np

# Define directories
raw_data_dir = 'data/raw'
processed_data_dir = 'data/processed'
os.makedirs(processed_data_dir, exist_ok=True)

GOOD_QC_FLAGS = ['1', '2']  # ARGO quality flags for good data

def process_argo_file(nc_file):
    ds = xr.open_dataset(nc_file)

    # Choose adjusted variables if they exist, otherwise raw
    temp_var = 'TEMP_ADJUSTED' if 'TEMP_ADJUSTED' in ds.data_vars else 'TEMP'
    psal_var = 'PSAL_ADJUSTED' if 'PSAL_ADJUSTED' in ds.data_vars else 'PSAL'
    pres_var = 'PRES_ADJUSTED' if 'PRES_ADJUSTED' in ds.data_vars else 'PRES'

    n_prof = ds.dims['N_PROF']
    n_levels = ds.dims['N_LEVELS']

    temp = ds[temp_var].values
    temp_qc = ds[temp_var + '_QC'].values.astype(str) if temp_var + '_QC' in ds.data_vars else np.array([['2']*n_levels]*n_prof)

    salinity = ds[psal_var].values
    salinity_qc = ds[psal_var + '_QC'].values.astype(str) if psal_var + '_QC' in ds.data_vars else np.array([['2']*n_levels]*n_prof)

    pressure = ds[pres_var].values

    lat = ds['LATITUDE'].values
    lon = ds['LONGITUDE'].values
    time = pd.to_datetime(ds['JULD'].values)

    cycle = ds['CYCLE_NUMBER'].values if 'CYCLE_NUMBER' in ds else [np.nan]*n_prof
    float_id = str(ds['PLATFORM_NUMBER'].values[0]) if 'PLATFORM_NUMBER' in ds else os.path.basename(nc_file)

    records = []
    for prof_idx in range(n_prof):
        for level_idx in range(n_levels):
            if (temp_qc[prof_idx, level_idx] in GOOD_QC_FLAGS and
                salinity_qc[prof_idx, level_idx] in GOOD_QC_FLAGS):
                records.append({
                    'float_id': float_id,
                    'cycle': cycle[prof_idx] if len(cycle) > prof_idx else np.nan,
                    'time': time[prof_idx] if len(time) > prof_idx else pd.NaT,
                    'lat': lat[prof_idx] if len(lat) > prof_idx else np.nan,
                    'lon': lon[prof_idx] if len(lon) > prof_idx else np.nan,
                    'pressure': pressure[prof_idx, level_idx],
                    'temperature': temp[prof_idx, level_idx],
                    'temp_qc': temp_qc[prof_idx, level_idx],
                    'salinity': salinity[prof_idx, level_idx],
                    'salinity_qc': salinity_qc[prof_idx, level_idx],
                })

    df = pd.DataFrame.from_records(records)
    return df

all_profiles = []

for filename in os.listdir(raw_data_dir):
    if filename.endswith('_prof.nc') or filename.endswith('prof.nc'):
        file_path = os.path.join(raw_data_dir, filename)
        print(f'Processing {filename}...')
        try:
            df_profile = process_argo_file(file_path)
            if df_profile is not None and not df_profile.empty:
                all_profiles.append(df_profile)
            else:
                print(f"No valid data found in {filename}")
        except Exception as e:
            print(f"Error processing {filename}: {e}")

if all_profiles:
    combined_df = pd.concat(all_profiles, ignore_index=True)
    output_csv = os.path.join(processed_data_dir, 'argo_profiles_cleaned.csv')
    combined_df.to_csv(output_csv, index=False)
    print(f'Processed {len(all_profiles)} profile files successfully.')
    print(f'Saved combined data to {output_csv}')
else:
    print("No valid profile data processed.")