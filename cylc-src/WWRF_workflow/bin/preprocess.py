#!/usr/bin/env python3
"""
Filename:    preprocess_data.py
Author:      Deanna Nash, dnash@ucsd.edu
Description: For W-WRF take wrfout and wrfcf and preprocess each individual lead time for the vars we need
"""

import os, sys
import argparse
from datetime import datetime
# import personal modules
from reader import load_WWRF_datasets

# Path to modules
import globalvars
globalvars.configure()

def main():
    parser = argparse.ArgumentParser(description="Preprocess WWRF data for specified init_date and lead_time")
    parser.add_argument("--leadtime", required=True, help="Step in forecast lead times (hours)")
    parser.add_argument("--outdir", type=str, default=globalvars.path_to_repo+"data/tmp/", help="Output NetCDF Directory")
    parser.add_argument("--init_date", required=True, help="the initialization date to preprocess in YYYYMMDDHH")
    args = parser.parse_args()

    F = args.leadtime
    outdir = args.outdir
    print(outdir)
    init_str = datetime.strptime(args.init_date, "%Y%m%dT%H00Z").strftime("%Y%m%d%H")
    model_name = "WWRF"
    
    #################################
    ### CHECK TO REMOVE TMP FILES ###
    #################################
    print('Removing tmp intermediate data files...') 
    # Specify the directory and the pattern
    fname = outdir+f"preprocess_F{F}.nc"  # Delete all intermediate preprocessed files
    try:
        os.remove(fname)
        print(f"Deleted: {fname}")
    except OSError as e:
        print(f"Error deleting {fname}: {e}")
    
    s = load_WWRF_datasets(F=F, tmp_directory=outdir, init_str=init_str)
    s.calc_vars()

if __name__ == "__main__":
    main()