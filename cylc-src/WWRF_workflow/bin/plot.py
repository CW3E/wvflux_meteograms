#!/usr/bin/env python3
"""
Filename:    plot.py
Author:      Deanna Nash, dnash@ucsd.edu
Description: Take each site-specific file (one lat/lon pair per .nc file) and create time-height plots for 3-day, 7-day, RH and WVFLUX
"""

import os, sys
import argparse
import xarray as xr
import pandas as pd
# Path to modules
sys.path.append('../../../modules/')
from plotter import plot_time_height_meteograms

def main():
    parser = argparse.ArgumentParser(description="Plot time-height meteograms using site-specific time series")
    parser.add_argument("--site", required=True, help="Site integer: values 0-424")
    parser.add_argument("--indir", type=str, default="/cw3e/mead/projects/cwp186/data/tmp/site_data/", help="site data directory")
    parser.add_argument("--outdir", type=str, default="/home/dnash/cwp140/figs/", help="Plot output directory")
    parser.add_argument("--pattern", default="site{site}.nc",
                        help="Filename pattern inside indir (default: site{site}.nc)")
    args = parser.parse_args()
    
    var_lst = ['r', 'wvflux']
    dur_lst = [7, 3]

    ## open the site data
    fname = os.path.join(args.indir, args.pattern.format(site=args.site))
    ds = xr.open_dataset(fname)
    lat = ds.latitude.values
    lon = ds.longitude.values
    model_name = "WWRF"

    for varname in var_lst:
        for dur in dur_lst:
            if dur == 7:
                ts = pd.timedelta_range(start='0 day', periods=29, freq='6h')
            else:
                ts = pd.timedelta_range(start='0 day', periods=25, freq='3h')
            subset_ds = ds.sel(step=ts)
                
            plot_time_height_meteograms(subset_ds, varname, lat, 360-lon, model_name, dur)

if __name__ == "__main__":
    main()