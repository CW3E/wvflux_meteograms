"""
Filename:    global_vars.py
Author:      Deanna Nash, dnash@ucsd.edu
Description: global variables such as path_to_data for all scripts
"""

path_to_repo = None

def configure():
    """
    Configure paths for the selected server.
    """

    global path_to_repo
    path_to_repo="/data/projects/operations/wvflux_meteograms/"