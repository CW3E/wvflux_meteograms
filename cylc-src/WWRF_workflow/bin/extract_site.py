#!/usr/bin/env python3
import argparse
import os
import xarray as xr
import numpy as np
import pandas as pd
from reader import load_WWRF_QPF
import globalvars

def main():
    parser = argparse.ArgumentParser(description="Extract site-specific time series from lead-time NetCDFs")
    parser.add_argument("--site", required=True, help="Site integer: values 0-424")
    parser.add_argument("--init_date", required=True, help="the initialization date to preprocess in YYYYMMDDHH")
    parser.add_argument("--indir", type=str, default=globalvars.path_to_repo+"data/tmp/", help="Directory containing per-leadtime NetCDF files")
    parser.add_argument("--outdir", type=str, default=globalvars.path_to_repo+"data/site_data/", help="Output directory")
    parser.add_argument("--pattern", default="preprocess_F{F}.nc",
                        help="Filename pattern inside indir (default: preprocess_F{F}.nc)")
    parser.add_argument("--leadmin", type=int, default=0, help="Minimum forecast lead time (hours)")
    parser.add_argument("--leadmax", type=int, default=168, help="Maximum forecast lead time (hours)")
    parser.add_argument("--leadstep", type=int, default=3, help="Step in forecast lead times (hours)")
    args = parser.parse_args()

    site = args.site
    init_str = args.init_date

    #################################
    ### CHECK TO REMOVE TMP FILES ###
    #################################
    print('Removing tmp intermediate data files...') 
    # Specify the directory and the pattern
    fname = args.outdir+f"site{site}.nc"  # Delete all intermediate preprocessed files
    try:
        os.remove(fname)
        print(f"Deleted: {fname}")
    except OSError as e:
        print(f"Error deleting {fname}: {e}")
    
    # collect datasets for each lead time
    datasets = []
    for F in range(args.leadmin, args.leadmax + 1, args.leadstep):
        fname = os.path.join(args.indir, args.pattern.format(F=F))
        if not os.path.exists(fname):
            print(f"Warning: missing file {fname}, skipping")
            continue

        ds = xr.open_dataset(fname)
        ds_site = ds.sel(location=int(site))
        datasets.append(ds_site)

    if not datasets:
        raise RuntimeError("No datasets found, nothing to save.")

    # concatenate along lead_time
    combined = xr.concat(datasets, dim="step")

    # open already processed QPF, select lat/lon, and merge datasets
    qpf = load_WWRF_QPF(init_str) ## read preprocessed qpf
    qpf_site = qpf.sel(location=int(site))
    
    ds = xr.merge([combined, qpf_site], compat='no_conflicts')
    td_index = pd.to_timedelta(ds.step.values, unit='h')
    # assign as the 'step' coordinate
    ds = ds.assign_coords(step=td_index)
    # ds["step"].attrs.update({"units": "hours", "description": "Forecast lead time"})
 
    # save site-specific file
    outname = f"{args.outdir}site{site}.nc"
    ds.to_netcdf(outname)
    print(f"Saved site-specific file to {args.outdir}")

if __name__ == "__main__":
    main()
