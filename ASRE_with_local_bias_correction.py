"""
@Author: Zied Ben Bouallegue (ECMWF)
"""
import time
import xarray as xr
import numpy as np
import pandas as pd

# add day of the year as dataset coordinate
def adddayofyear(ds):
    if "dayofyear" not in ds.coords:
        dayofyear = ds.time.dt.dayofyear.data
        ds.coords["dayofyear"] = ("time", dayofyear)
        ds.coords["dayofyear"].attrs["long_name"] = "day of the year"
    return ds

# selection of dat of year +- wiw days around a given date
def selectdayofyear(date,wiw,dataset):
    doy = pd.to_datetime(str(date)).dayofyear
    lim1 = doy - wiw 
    if lim1 < 1:
       lim1_r = 365 + lim1 
    else:
       lim1_r = 366
    lim2 = doy + wiw     
    if lim2 > 365:
       lim2_r = lim2-365
    else:
       lim2_r = 0
    doy_h = dataset.dayofyear
    idoy =  ((doy_h > lim1) & (doy_h < lim2)) | (doy_h < lim2_r) | (doy_h > lim1_r)            
    return idoy

# Representativness uncertainty parameters 
# function of deltax, the model grid resolution (in km)
def UncTwoMeterTemperature(deltax) :
        beta0 = min(0.02*deltax,2.)
        beta1 = max(0.35 -0.002*deltax,0.15)
        powtr = 0.25
        sigma = [ beta0, beta1, powtr ] 
        return sigma 


print("Apply ASRE")
start_time =time.time()

# get data
print("1. get data")
fcs_tr = xr.open_dataarray('ESSD_benchmark_training_data_forecasts.nc')
obs_tr = xr.open_dataarray('ESSD_benchmark_training_data_observations.nc')
fcs = xr.open_dataarray('ESSD_benchmark_test_data_forecasts.nc')

# add day of year as coordinate
fcs_tr = adddayofyear(fcs_tr)
fcs = adddayofyear(fcs)

# bias correction for each station and lead time seperately 
# estimate mean error over the past 20 years 
print("2. correct bias")
wiw= 30 # +- window around verification date (in days)
dates = np.array(fcs.time)
for idate,date_in in enumerate(dates):
    idoy = selectdayofyear(date_in,wiw,fcs_tr)
    fcs_tr_sel = fcs_tr.sel(time= fcs_tr.time[idoy])
    fcs_tr_mean = fcs_tr_sel.mean(("time","year","number")).data
    obs_tr_mean = obs_tr.sel(time=fcs_tr_sel.time).mean(("time","year")).data  
    bias_tr = np.tile( (fcs_tr_mean - obs_tr_mean).flatten(), (len(fcs.number),1)).T
    fcs[:,idate,:,:]-= bias_tr.reshape((fcs.shape[0],fcs.shape[2],fcs.shape[3]))
   
# forecast dressing to account for representativness uncertainty
# using a universal model
# see ECMWF Tech Memo 865 (in particular Eq 4)
print("3. account for representativeness uncertainty")
deltax=18 # grid resolution (in km) 
sigma = UncTwoMeterTemperature(deltax)
var = sigma[0] + sigma[1]*abs(fcs.model_altitude - fcs.station_altitude)**sigma[2]
ns = len(np.array(fcs[0,:,:,0]).flatten())
for j in range(fcs.shape[3]): 
    for i in range(fcs.shape[0]): 
        fcs[i,:,:,j] += np.random.normal(0, var[i], size = ns).reshape(fcs[0,:,:,0].shape)

print("4. archive in netcdf")
fcs.to_netcdf('ESSD_benchmark_test_ASRE.nc')  

end_time = time.time()
print('Time elapsed:')
print(str((end_time - start_time) / 60) + ' minutes elapsed.')

print("done")
