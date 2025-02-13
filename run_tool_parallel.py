"""
Filename:    run_tool_parallel.py
Author:      Deanna Nash, dnash@ucsd.edu
Description: For GFS, and ECMWF: output .png files of time-height meteograms plot for different lat/lons.
"""
import os
import sys
import glob
import numpy as np
import pandas as pd
from datetime import datetime
import netCDF4
import xarray as xr
import multiprocessing as mp

from read_deterministic_data import load_GFS_datasets, load_ECMWF_datasets, read_preprocessed_IVT_data
from calc_funcs import format_timedelta_to_HHMMSS
from cw3e_tools import remove_tmp_data_files
from plotter import plot_time_height_meteograms

def debug_print(message): 
    if(debugFlag == True):
        print(message, flush=True)

def multiP_preprocess_intermediate(F):
    '''
    Prepares intermediate data
    '''
    print('... Loading data for {0} hour lead'.format(F))
    if model_name == 'ECMWF':
        s = load_ECMWF_datasets(F=F, fdate=fdate)
        model_data = s.calc_vars()

    elif model_name == 'GFS':
        s = load_GFS_datasets(F=F, fdate=fdate)
        model_data, tmp = s.calc_vars()
        
def subset_ds_func(ds, lat, lon, duration, model_name):
    if (duration == 7) & (model_name == 'ECMWF'):
        ts = pd.timedelta_range(start='0 day', periods=29, freq='6H')
        xtick_dur = 2
    elif (duration == 7) & (model_name == 'GFS'):
        ts = pd.timedelta_range(start='0 day', periods=57, freq='3H')
        xtick_dur = 4
    else:
        ts = pd.timedelta_range(start='0 day', periods=25, freq='3H')
        xtick_dur = 2
    
    ## subset to current point and duration length
    ds = ds.sel(latitude=lat, longitude=lon, step=ts, method='nearest')
    
    return ds

def multiP_create_time_height_meteograms(argval):    
    subset_ds, lon, lat, varname, dur, model_name = argval
    debug_print('plotting {3}-day {2} at {0}N, {1}W'.format(lat, lon, varname, dur))
    plot_time_height_meteograms(subset_ds, varname, lat, 360-lon, model_name, dur)
    debug_print('plotting {3}-day {2} at {0}N, {1}W'.format(lat, lon, varname, dur))

debugFlag = True # set to False to remove most of the print statements

if __name__ == '__main__':  
    model_name = sys.argv[1]
    fdate = sys.argv[2] ## set this to None to get most recently downloaded data    
    
    start_time = pd.Timestamp.today()
    print('Creating WV Flux Meteograms for {0}'.format(model_name))

    ## FIRST LOOP - LEAD TIME ##
    if model_name == 'ECMWF':
        arr1 = np.arange(0, 72+3, 3)
        arr2 = np.arange(78, 168+6, 6)
        F_lst = np.concatenate((arr1, arr2), axis=0)
    elif model_name == 'GFS':
        F_lst = np.arange(0, 168+3, 3)

    #################################
    ### CHECK TO REMOVE TMP FILES ###
    #################################
    print('Removing tmp intermediate data files...') 
    # Specify the directory and the pattern
    # tmp_directory = "/home/dnash/comet_data/tmp/"
    tmp_directory = "/data/projects/operations/wvflux_meteograms/data/tmp/"
    pattern = "tmp_{0}*.nc".format(model_name)  # Delete all tmp files
    remove_tmp_data_files(tmp_directory, pattern)

    ############################################
    ### PREPROCESS INTERMEDIATE GFS OR ECMWF ###
    ############################################
    print('...preprocess intermediate data ...')

    with mp.get_context('spawn').Pool(processes=30) as pool:
        debug_print("Via map with exception")
        debug_print("\tKicking off pool via map with exception")
        pool.map(multiP_preprocess_intermediate,F_lst)
        debug_print("\tKicked off pool via map with exception")
        pool.close()
        pool.join()

    ##############################
    ### LOAD INTERMEDIATE DATA ###
    ##############################
    files = glob.glob(tmp_directory + 'tmp_{0}_*.nc'.format(model_name))
    sorted_files = sorted(files)
    ds = xr.open_mfdataset(sorted_files, engine='netcdf4', concat_dim="step", combine='nested')

    ## need to fix precipitation
    if model_name == 'ECMWF':
        tp = ds.tp.fillna(0) # make sure nan at beginning is 0 to do calculation right
        tp = tp.diff(dim='step') # calculate difference between time steps
        ds = ds.drop_vars(["tp"]) # get rid of old tp (accumulated variable)
        ds = xr.merge([ds, tp]) # merge dataset with new tp

    if model_name == 'GFS':
        ts_3hr = pd.timedelta_range(start='0 day', periods=57, freq='3H')
        ts_6hr = pd.timedelta_range(start='0 day', periods=29, freq='6H')
        tp = ds.tp ## pull out tp
        prec_3hr = tp.sel(step=ts_3hr[1::2]) ## grab only the 3hr values
        tp2 = tp.diff(dim='step') ## calculate difference in precip
        ## the values for 6hr timesteps are correct, the values for 3hr timesteps are incorrect
        prec_6hr = tp2.sel(step=ts_6hr[1:]) # grab only the 6hr values
        new_prec = prec_3hr.combine_first(prec_6hr) # combine the correct 3hr values with the correct 6hr values
        ds = ds.drop_vars(["tp"]) # get rid of old tp (accumulated variable)
        ds = xr.merge([ds, new_prec]) # merge dataset with new tp

    ivt = read_preprocessed_IVT_data(model=model_name, F_lst=F_lst, fdate=pd.to_datetime(ds.time.values).strftime('%Y%m%d%H'))
    ds = ds.assign(ivt=(['step','latitude','longitude'],ivt.ivt.values))
    ## load ds into memory
    ds = ds.load()

    ###############################################
    ### CREATE ARGUMENT LIST FOR CREATING PLOTS ###
    ###############################################
    lat_lst = np.arange(26, 51, 1)
    lon_lst = np.arange(111, 128, 1)
    var_lst = ['r', 'wvflux']
    dur_lst = [7, 3]

    arglst_USWEST = []
    for i, x in enumerate(lon_lst):
        for j, y in enumerate(lat_lst):
            for k, varname in enumerate(var_lst):
                for l, dur in enumerate(dur_lst):
                    subset_ds = subset_ds_func(ds, y, x, dur, model_name)
                    arglst_USWEST.append((subset_ds, x,y, varname, dur, model_name))

    lat_lst = np.arange(51, 70, 1)
    lon_lst = np.arange(130, 175, 1)               
    arglst_AK = []
    for i, x in enumerate(lon_lst):
        for j, y in enumerate(lat_lst):
            for k, varname in enumerate(var_lst):
                for l, dur in enumerate(dur_lst):
                    subset_ds = subset_ds_func(ds, y, x, dur, model_name)
                    arglst_AK.append((subset_ds, x,y, varname, dur, model_name))

    final_arglst = arglst_USWEST + arglst_AK

    del ds

    ###################################
    ### CREATE PLOTS USING POOL.MAP ###
    ###################################

    print('...create plots ...')

    # mp.set_start_method('spawn', force=True)    
    # with mp.Pool(processes=16) as pool:
    with mp.get_context('spawn').Pool(processes=16) as pool:
        debug_print("Via map with exception")
        debug_print("\tKicking off pool via map with exception")
        pool.map(multiP_create_time_height_meteograms,final_arglst)
        debug_print("\tKicked off pool via map with exception")
        pool.close()
        pool.join()


    end_time = pd.Timestamp.today()
    td = end_time - start_time
    td = format_timedelta_to_HHMMSS(td)
    print('Plots for {0} took {1} to run'.format(model_name, td))

    ########################
    ### REMOVE TMP FILES ###
    ########################
    print('Removing tmp intermediate data files...') 
    # Specify the directory and the pattern
    pattern = "tmp_{0}*.nc".format(model_name)  # Delete all tmp files
    remove_tmp_data_files(tmp_directory, pattern)
        
    