from argopy import DataFetcher

# Try a well-populated float
try:
    ds = DataFetcher().float(1902785).to_xarray()
    print(ds)
    print(ds.data_vars)
    print("LAT:", ds['LATITUDE'].values)
    print("LON:", ds['LONGITUDE'].values)
    print("PRES:", ds['PRES'].values)
    print("TEMP:", ds['TEMP'].values)
    print("PSAL:", ds['PSAL'].values)
except Exception as e:
    print("Error loading data:", e)

