"""
Filename:    cw3ecmaps.py
Author:      Deanna Nash, dnash@ucsd.edu
Description: Functions for cmaps from the CW3E website adapted from from https://github.com/samwisehawkins/nclcmaps
"""

import numpy as np
import matplotlib.colors as mcolors
from matplotlib.colors import ListedColormap
from matplotlib.ticker import FuncFormatter

__all__ = ['cw3ecmaps']


cw3e_cmaps =    {
                
                 "wvflux":{
                        "colors":[[255, 255, 51], # 0.025-0.05
                                [255, 234, 51], # 0.05-0.075
                                [255, 211, 51], # 0.075-0.1
                                [255, 189, 50], # 0.1-0.15
                                [255, 155, 51], # 0.15-0.2
                                [255, 115, 51], # 0.2-0.25
                                [255, 75, 51], # 0.25-0.3
                                [239, 51, 63], # 0.3-0.35
                                [214, 51, 83], # 0.35-0.4
                                [181, 51, 110], # 0.4-0.45
                                [161, 51, 127], # 0.45-0.5
                                [140, 51, 143], # 0.5+
                                 ],
                        "bounds":[0.025, 0.05, 0.075, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 1.],
                        "ticks":[0.025, 0.05, 0.075, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5],
                        "label":'WV Flux (m s$^{-1}$)',
                        },
    
                "r":{
                        "colors":[[255, 255, 255], # <50
                                [210, 176, 61], # 50-55
                                [227, 211, 122], # 55-60
                                [249, 244, 197], # 60-65
                                [209, 240, 137], # 65-70
                                [188, 238, 104], # 70-75
                                [175, 225, 84], # 75-80
                                [163, 214, 65], # 80-85
                                [142, 194, 49], # 85-90
                                [102, 159, 45], # 90-95
                                [82, 142, 44], # 95-100
                                 ],
                        "bounds":[0, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 200],
                        "ticks":[50, 55, 60, 65, 70, 75, 80, 85, 90, 95],
                        "label":'Relative Humidity (%)',
                        },
    


                }
                  
def cmap(cbarname):
        data = np.array(cw3e_cmaps[cbarname]["colors"])
        data = data / np.max(data)
        cmap = ListedColormap(data, name=cbarname)
        bnds = cw3e_cmaps[cbarname]["bounds"]
        norm = mcolors.BoundaryNorm(bnds, cmap.N)
        cbarticks = cw3e_cmaps[cbarname]["ticks"]
        cbarlbl = cw3e_cmaps[cbarname]["label"]
        return cmap, norm, bnds, cbarticks, cbarlbl


