#!/usr/bin/python3
"""
Filename:    cw3e_tools.py
Author:      Deanna Nash, dnash@ucsd.edu
Description: a collection of useful constants, colors, useful plotting and loading etc.
"""

import os
import re
import shutil
import subprocess
import glob


def remove_tmp_data_files(directory, pattern):

    # Find all matching files
    files = glob.glob(os.path.join(directory, pattern))

    # Delete each file
    for file_path in files:
        try:
            os.remove(file_path)
            print(f"Deleted: {file_path}")
        except OSError as e:
            print(f"Error deleting {file_path}: {e}")