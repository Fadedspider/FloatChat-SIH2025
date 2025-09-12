import xarray as xr
ds = xr.open_dataset("nodc_4903326_prof.nc")
print(ds)
print(ds.data_vars)
import matplotlib.pyplot as plt
import numpy as np

prof = 0  # choose first profile (can try prof = 1, 2, ... 7)

pres = ds['pres_adjusted'].values[prof]
temp = ds['temp_adjusted'].values[prof]
qc = ds['temp_adjusted_qc'].values[prof].astype(str)

# Only plot "good" data
good = np.isin(qc, ['1', '2'])

plt.figure()
plt.plot(temp[good], pres[good])
plt.gca().invert_yaxis()
plt.title(f"Profile {prof+1}: Temp vs Depth")
plt.xlabel('Temperature (°C)')
plt.ylabel('Pressure (dbar)')
plt.show()


print(ds['juld'].values)         # Timestamps for all 8 profiles
print(ds['latitude'].values)     # Latitudes
print(ds['longitude'].values)    # Longitudes


for prof in range(ds.dims['n_prof']):
    pres = ds['pres_adjusted'].values[prof]
    temp = ds['temp_adjusted'].values[prof]
    qc = ds['temp_adjusted_qc'].values[prof].astype(str)
    good = np.isin(qc, ['1', '2'])
    plt.plot(temp[good], pres[good], label=f"P{prof+1}")
plt.gca().invert_yaxis()
plt.title('All Profiles: Temp vs Depth')
plt.xlabel('Temperature (°C)')
plt.ylabel('Pressure (dbar)')
plt.legend()
plt.show()

for prof in range(ds.dims['n_prof']):
    pres = ds['pres_adjusted'].values[prof]
    psal = ds['psal_adjusted'].values[prof]
    qc = ds['psal_adjusted_qc'].values[prof].astype(str)
    good = np.isin(qc, ['1', '2'])
    plt.plot(psal[good], pres[good], label=f"P{prof+1}")
plt.gca().invert_yaxis()
plt.title('All Profiles: Salinity vs Depth')
plt.xlabel('Salinity (PSU)')
plt.ylabel('Pressure (dbar)')
plt.legend()
plt.show()
for prof in range(ds.dims['n_prof']):
    pres = ds['pres_adjusted'].values[prof]
    temp = ds['temp_adjusted'].values[prof]
    psal = ds['psal_adjusted'].values[prof]
    temp_qc = ds['temp_adjusted_qc'].values[prof].astype(str)
    psal_qc = ds['psal_adjusted_qc'].values[prof].astype(str)
    good_temp = np.isin(temp_qc, ['1', '2'])
    good_psal = np.isin(psal_qc, ['1', '2'])
    good = good_temp & good_psal
    plt.plot(temp[good], psal[good], label=f"P{prof+1}")