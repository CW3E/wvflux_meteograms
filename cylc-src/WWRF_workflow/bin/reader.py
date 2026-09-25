#!/usr/bin/python3
"""
Filename:    read_deterministic_data.py
Author:      Deanna Nash, dnash@ucsd.edu
Description: functions to read deterministic data from GFS, ECMWF
"""

import sys
import os
import gc
import glob
import shutil
import subprocess
import re
import xarray as xr
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import cartopy.crs as ccrs
from netCDF4 import Dataset
from wrf import getvar

# Path to modules
import globalvars
globalvars.configure()
sys.path.append(f"{globalvars.path_to_repo}modules")
import calc_funcs as cfuncs

def find_nearest_indices(ds, lat, lon):
    # Function to find nearest grid indices on 2D curvilinear grid
    dist = (ds['latitude'] - lat)**2 + (ds['longitude'] - lon)**2
    iy, ix = np.unravel_index(dist.argmin(), dist.shape)
    return iy, ix

def subset_wwrf_ds(ds):
    # NPAC Locations
    lat_lst = np.arange(26, 51, 1)
    lon_lst = np.arange(360 - 128, 360 - 111, 1)

    # SEAK Locations
    lat_lst2 = np.arange(51, 60, 1)
    lon_lst2 = np.arange(360 - 141, 360 - 130, 1)

    # Build Cartesian products for each set separately
    lat_grid, lon_grid = np.meshgrid(lat_lst, lon_lst, indexing="ij")
    lat_grid2, lon_grid2 = np.meshgrid(lat_lst2, lon_lst2, indexing="ij")

    # Flatten and concatenate the two sets
    lats = np.concatenate([lat_grid.ravel(), lat_grid2.ravel()])
    lons = np.concatenate([lon_grid.ravel(), lon_grid2.ravel()])

    # Get indices for all requested points
    indices = [find_nearest_indices(ds, la, lo) for la, lo in zip(lats, lons)]
    iy = [i[0] for i in indices]
    ix = [i[1] for i in indices]

    # Subset the dataset
    subset = ds.isel(
        y=xr.DataArray(iy, dims="location"),
        x=xr.DataArray(ix, dims="location")
    )

    # Attach the requested coordinates to the new "location" dimension
    subset = subset.assign_coords(
        location=np.arange(len(lats)),
        latitude=("location", lats),
        longitude=("location", lons)
    )

    return subset

def read_wwrf_deterministic(filename, vardict):
    '''
    author: Ricardo Vilela
    email: rbatistavilela@ucsd.edu

    function usage:
    
    filename example:
    wrfcf_gfs_d01_2024-06-11_23_00_00.nc

    vardict example:

    vardict = {
            "uivt":{"varname":'IVTU'}, #U-component of IVT
            "vivt":{"varname":'IVTV'}, #V-component of IVT
            "ivt":{"varname":'IVT'},#Integrated vapor transport
            "slp":{"varname":'slp'} #sea level pressure

        }
    Output:
    Dictionary of objects for each variable set in the vardict argument. Ex.
    ivt = selected_vars["ivt"].values


    '''
    print('[INFO] reading WWRF file: '+filename)
    selected_vars = {}
    ds = xr.open_dataset(filename)
 
    ##iterating over all variables in the vardict and storing each one in a new dictionary called selected_vars
    for var in vardict.keys():
        var_ds = ds[vardict[var]["varname"]]  
        var_ds = var_ds.assign_coords(valid_time=('time', ds["time"].values))
        var_ds["time"]=ds["forecast_reference_time"]
        var_ds = var_ds.rename({'lat': 'latitude', 'lon':'longitude'})
        ##converting -180 to 180 format to 0 360 to match ecmwf and gfs
        longitude_360 = np.where(var_ds.longitude.values < 0, var_ds.longitude.values + 360, var_ds.longitude.values)
        var_ds.longitude.values=longitude_360
        if var_ds.shape[0]==1:
            selected_vars[var] = var_ds[0,:,:]
        else:
            print('[ERROR] multiple values for timedimension')
            exit()

    ds.close()
    del ds
        
    return selected_vars


def read_wwrfout_deterministic(filename, vardict):
    '''
    author: Ricardo Vilela
    email: rbatistavilela@ucsd.edu

    function usage:
    
    filename example:
    wrfcf_gfs_d01_2024-06-11_23_00_00.nc

    vardict example:

    vardict = {
            "uivt":{"varname":'IVTU'}, #U-component of IVT
            "vivt":{"varname":'IVTV'}, #V-component of IVT
            "ivt":{"varname":'IVT'},#Integrated vapor transport
            "slp":{"varname":'slp'} #sea level pressure

        }
    Output:
    Dictionary of objects for each variable set in the vardict argument. Ex.
    ivt = selected_vars["ivt"].values


    '''
    print('[INFO] reading WWRF file: '+filename)
    selected_vars = {}
    ds = Dataset(filename)

    ##iterating over all variables in the vardict and storing each one in a new dictionary called selected_vars
    for var in vardict.keys():
        var_ds = getvar(ds, vardict[var]["varname"])   

        try:
            longitude_360 = np.where(var_ds.XLONG.values < 0, var_ds.XLONG.values + 360, var_ds.XLONG.values)
            var_ds.XLONG.values=longitude_360
        except:
            try:
                longitude_360 = np.where(var_ds.XLONG_U.values < 0, var_ds.XLONG_U.values + 360, var_ds.XLONG_U.values)
                var_ds.XLONG_U.values=longitude_360
            except:
                try:
                    longitude_360 = np.where(var_ds.XLONG_V.values < 0, var_ds.XLONG_V.values + 360, var_ds.XLONG_V.values)
                    var_ds.XLONG_V.values=longitude_360
                except:
                    print('[ERROR] Longitude variable unknown')
                    exit()
        selected_vars[var] = var_ds
        # if var_ds.shape[0]==1:
            # selected_vars[var] = var_ds[0,:,:]
        # else:
            # print('[ERROR] multiple values for timedimension')
            # exit()

    ## close the dataset you opened
    ds.close()
    del ds
        
    return selected_vars

class load_WWRF_datasets:
    '''
    Loads variables needed for ivt cross section plots from CF and WRFOUT WRF files
    
    Parameters
    ----------
    F : int
        the forecast lead requested
        
    init_str : str
        string of date for the initialization date in YYYYMMDDHH format
  
    Returns
    -------
    netCDF : 
        saved netCDF tmp intermediate data file
    
    '''
    def __init__(self, F, tmp_directory, model, init_str):
        self.F = int(F)
        ## get model name
        model_dirs = {
            "WWRF_gfs": "gfs",
            "WWRF_ecmwf": "ecmwf",
        }
        
        if model not in model_dirs:
            raise ValueError(
                f"Unsupported model '{model}'. "
                f"Expected one of: {list(model_dirs)}"
            )

        self.model = model
        self.model_name = model_dirs[model]

        # Validate and parse initialization time
        try:
            init_time = datetime.strptime(init_str, "%Y%m%d%H")
        except ValueError as exc:
            raise ValueError(
                f"Invalid initialization time '{init_str}'. "
                "Expected format YYYYMMDDHH."
            ) from exc
        
        # Calculate valid time
        valid_time = init_time + timedelta(hours=self.F)
        
        valid_time_str = valid_time.strftime("%Y-%m-%d_%H_%M_%S")

        # get WY
        if init_time.month >= 10:
            season = f"{init_time.year}-{init_time.year + 1}"
        elif init_time.month <= 3:
            season = f"{init_time.year - 1}-{init_time.year}"
        else:
            raise ValueError(
                f"Initialization date {init_time:%Y-%m-%d} is outside the "
                "October-March season."
            )
        
        data_root = Path(
            f"/cw3e/mead/datasets/cw3e/NRT/{season}/NRT_{self.model_name}"
        )
        
        fpath = data_root / init_str
        
        self.wwrf_cf_filename = str(
            fpath / f"cf/wrfcf_{self.model_name}_d01_{valid_time_str}.nc"
        )
    
        self.wwrfout_filename = str(
            fpath / f"wrfout/wrfout_d01_{valid_time_str}"
        )
        
        self.tmp_dir = tmp_directory
        
    def calc_vars(self):
        ##################################
        ### CREATE 2D DS from CF FILES ###
        ##################################
        
        ## variables to read from cf files
        ## IVT, IWV, freezing level, surface pressure, terrain height
        
        wwrf_vardict = {
                    "ivt":{"varname":'IVT'},#Integrated vapor transport
                    "iwv":{"varname":'IWV'},#Integrated water vapor
                    "freezing_level":{"varname":'z0c'}, #freezing level
                    "sfc_pressure":{"varname":'p_sfc'}, #surface pressure
                    "orog":{"varname":'Z_sfc'}, #terrain height
        
                }
        
        #wwrf is a dictionary of datasets
        wwrf = read_wwrf_deterministic(filename=self.wwrf_cf_filename,vardict=wwrf_vardict)
        da_lst = [wwrf['ivt'], wwrf['iwv'], wwrf['freezing_level'], wwrf['sfc_pressure'], wwrf['orog']]
        ds_2D = xr.merge(da_lst, compat='no_conflicts')
        
        ## rename vars to be consistent with ECMWF and GFS
        rename_dict = {"IVT": "ivt", "IWV": "pwat", "z0c":"gh", "p_sfc":"sp", "Z_sfc":"orog"}
        ds_2D = ds_2D.rename(rename_dict)
        
        # Create 'step' coordinate in hours
        ds_2D = ds_2D.assign_coords(
            step=((ds_2D["valid_time"] - ds_2D["time"]) / np.timedelta64(1, "h"))
        )
        
        # drop x and y coord variables
        ds_2D = ds_2D.drop_vars(["x", "y"])
        
        ######################################
        ### CREATE 3D DS from WRFOUT FILES ###
        ######################################
        ## getvar dict for loading WRF variables
        wwrf_vardict = {
            "u_wind": {"varname":"ua"}, #U-component of wind
            "v_wind": {"varname":"va"}, #U-component of wind
            "temperature": {"varname":"tc"}, #Temperature in Cel
            "rh":{"varname":"rh"}, #Relative Humidity
            "pres": {"varname": "pres"} ## pressure on model levels
        }
        
        wwrf = read_wwrfout_deterministic(self.wwrfout_filename, wwrf_vardict)
        
        # calculating specific humidity from relative humidity
        # temp needs to be in K - convert from C to K by +273.15
        # pressure needs to be in Pa, so that is all good
        # rh needs to be a fraction (e.g. 0.5 for 50%)
        q = cfuncs.specific_humidity(temperature=wwrf["temperature"].values+273.15, pressure=wwrf["pres"].values, relative_humidity=wwrf["rh"].values/100)
        
        ## calculating wvflux
        density = cfuncs.calculate_air_density(pressure=wwrf["pres"], temperature=wwrf["temperature"], relative_humidity=wwrf['rh'])
        
        wv_flux = cfuncs.calculate_wvflux(uwind=wwrf["u_wind"].values, vwind=wwrf["v_wind"].values, density=density, specific_humidity=q)
        
        
        ### create a 3D dataset with all the vars we need
        coords={
            "bottom_top":(("z"), np.arange(0,99,1)),
            "latitude":(("y", "x"), wwrf["pres"].XLAT.values), 
            "longitude":(("y", "x"), wwrf["pres"].XLONG.values),
            "time":((), wwrf["pres"].Time.values - wwrf["pres"].XTIME.values * np.timedelta64(1, "m")),
            "valid_time":((), wwrf["pres"].Time.values),
            "step":((), (wwrf["pres"].XTIME.values * np.timedelta64(1, "m")) / np.timedelta64(1, "h")),
               }
        
        
        data = {
            "u": (("z", "y", "x"), wwrf["u_wind"].values),
            "v": (("z", "y", "x"), wwrf["v_wind"].values),
            "pressure": (("z", "y", "x"), wwrf["pres"].values),
            "r": (("z", "y", "x"), wwrf["rh"].values),
            "t": (("z", "y", "x"), wwrf["temperature"].values),
            "wvflux": (("z", "y", "x"), wv_flux),
        }
        
        ds_3D = xr.Dataset(data, coords=coords)

        ## creating a 3D time array for plotting
        a = ds_3D.valid_time
        b = ds_3D["u"]
        a2, b2 = xr.broadcast(a, b)
        a2.name = 'valid_time_td'
        ds_3D['valid_time_td'] = a2
        
        ###############################################
        ### MERGE TOGETHER TO CREATE SINGLE DATASET ###
        ###############################################
        ds = xr.merge([ds_2D, ds_3D], compat='override')

        ## clean up unnecessary data
        del wwrf, q, density, wv_flux, ds_2D, ds_3D, da_lst
        gc.collect()

        subset = subset_wwrf_ds(ds)

        ## clean up after subsetting
        del ds
        gc.collect()
        
        ####################################
        ## write intermediate data files ###
        ####################################
        out_fname = self.tmp_dir + f'preprocess_{self.model}_F{self.F}.nc'
        subset.to_netcdf(path=out_fname, mode = 'w', format='NETCDF4')
        subset.close() ## close data

        gc.collect()
    
        return None

def load_WWRF_QPF(fdate, model):
    model_dirs = {
            "WWRF_gfs": "gfs",
            "WWRF_ecmwf": "ecmwf",
        }
        
    if model not in model_dirs:
        raise ValueError(
            f"Unsupported model '{model}'. "
            f"Expected one of: {list(model_dirs)}"
        )
    
    model_name = model_dirs[model]

    ### LOAD QPF data
    fpath = f"/cw3e/mead/datasets/cw3e/NRT/2025-2026/NRT_{model_name}/{fdate}/QPF_output/"
    filename = f"West-WRF_{model_name}_1hQPF_9km_{fdate}_F1-240.nc"
    
    qpf = xr.open_dataset(fpath+filename)
    
    init_time = np.datetime64(datetime.strptime(fdate, "%Y%m%d%H"))
    F = qpf.ftimes.values
    valid_times = init_time + F.astype("timedelta64[h]")
    
    ### create a dataset with 3-hourly accumulated precipitation
    ### this needs to match the coords of the loaded intermediate data to merge
    coords={
        "latitude":(("y", "x"), qpf.lat.values), 
        "longitude":(("y", "x"), qpf.lon.values),
        "time":((), init_time),
        "valid_time":(("step"), valid_times),
        "step":(("step"), F.astype(np.float32)),
           }
    
    data = {
        "tp": (("step", "y", "x"), qpf["QPF_Acc"].values),
    }
    
    qpf = xr.Dataset(data, coords=coords)
    qpf = qpf.sel(step=np.arange(3, 168+3, 3, dtype=np.float32))
    qpf = subset_wwrf_ds(qpf)
    return qpf