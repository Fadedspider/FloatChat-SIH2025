import xarray as xr

file_path = 'data/raw/nodc_2902206_prof.nc'  # example file
ds = xr.open_dataset(file_path)

print(ds.data_vars)  # lists all data variable names in the file
print(ds)            # detailed summary of dataset contents
