#!/usr/bin/python3
"""
Filename:    plotter.py
Author:      Deanna Nash, dnash@ucsd.edu and Ricardo Vilela, rbatistavilela@ucsd.edu
Description: Functions for plotting IVT cross sections
"""

import os, sys
import numpy as np
import xarray as xr
import matplotlib as mpl
mpl.use('agg') ## for speedup
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter
import matplotlib.ticker as mticker
import colorsys
from datetime import datetime, timedelta
from matplotlib.colors import LinearSegmentedColormap # Linear interpolation for color maps
import matplotlib.patches as mpatches
from matplotlib import cm, colors as clr
from matplotlib.colorbar import Colorbar # different way to handle colorbar
import pandas as pd
from matplotlib.gridspec import GridSpec
import itertools
from PIL import Image
from matplotlib import font_manager as fm
import matplotlib.ticker as ticker
from matplotlib.ticker import FuncFormatter
from matplotlib.ticker import MaxNLocator
from matplotlib.dates import HourLocator
from scipy.ndimage import gaussian_filter
import copy
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
import cw3ecmaps as ccmaps

def roundPartial(value, resolution):
    return np.round(value / resolution) * resolution

def set_cw3e_font(current_dpi, scaling_factor):
    fm.fontManager.addfont('/home/cw3eit/ARPortal/gefs/scripts/ar_landfall_tool/utils/fonts/helvetica.ttc')

    plt.rcParams.update({
                    'font.family' : 'Helvetica',
                    'figure.dpi': current_dpi,
                    'font.size': 8 * scaling_factor, #changes axes tick label
                    'axes.labelsize': 8 * scaling_factor,
                    'axes.titlesize': 8 * scaling_factor,
                    'xtick.labelsize': 8 * scaling_factor,#do nothing
                    'ytick.labelsize': 8 * scaling_factor, #do nothing
                    'legend.fontsize': 5 * scaling_factor,
                    'lines.linewidth': 0.7 * scaling_factor,
                    'axes.linewidth': 0.2 * scaling_factor,
                    'legend.fontsize': 12 * scaling_factor,
                    'xtick.major.width': 0.8 * scaling_factor,
                    'ytick.major.width': 0.8 * scaling_factor,
                    'xtick.minor.width': 0.6 * scaling_factor,
                    'ytick.minor.width': 0.6 * scaling_factor,
                    'lines.markersize': 6 * scaling_factor
                })

def plot_cw3e_logo(ax, orientation):
    ## location of CW3E logo
    if orientation == 'horizontal':
        im = '/common/CW3E_Logo_Suite/1-Horzontal-PRIMARY_LOGO/Digital/JPG-RGB/CW3E-Logo-Horizontal-FullColor-RGB.jpg'
    else:
        im = '/common/CW3E_Logo_Suite/5-Vertical-Acronym_Only/Digital/PNG/CW3E-Logo-Vertical-Acronym-FullColor.png'
    img = np.asarray(Image.open(im))
    ax.imshow(img)
    ax.axis('off')
    return ax


def draw_basemap(ax, datacrs=ccrs.PlateCarree(), extent=None, xticks=None, yticks=None, grid=False, left_lats=True, right_lats=False, bottom_lons=True, mask_ocean=False, coastline=True):
    """
    Creates and returns a background map on which to plot data. 
    
    Map features include continents and country borders.
    Option to set lat/lon tickmarks and draw gridlines.
    
    Parameters
    ----------
    ax : 
        plot Axes on which to draw the basemap
    
    datacrs : 
        crs that the data comes in (usually ccrs.PlateCarree())
        
    extent : float
        Set map extent to [lonmin, lonmax, latmin, latmax] 
        Default: None (uses global extent)
        
    grid : bool
        Whether to draw grid lines. Default: False
        
    xticks : float
        array of xtick locations (longitude tick marks)
    
    yticks : float
        array of ytick locations (latitude tick marks)
        
    left_lats : bool
        Whether to add latitude labels on the left side. Default: True
        
    right_lats : bool
        Whether to add latitude labels on the right side. Default: False
        
    Returns
    -------
    ax :
        plot Axes with Basemap
    
    Notes
    -----
    - Grayscale colors can be set using 0 (black) to 1 (white)
    - Alpha sets transparency (0 is transparent, 1 is solid)
    
    """
    ## some style dictionaries
    kw_ticklabels = {'color': 'black', 'weight': 'light'}
    kw_grid = {'linewidth': 0.6, 'color': 'k', 'linestyle': '--', 'alpha': 0.4}
    kw_ticks = {'length': 4, 'width': 0.5, 'pad': 2, 'color': 'black',
                             'labelcolor': 'dimgray'}

    # Use map projection (CRS) of the given Axes
    mapcrs = ax.projection    
    
    # Add map features (continents and country borders)
    ax.add_feature(cfeature.LAND, facecolor='0.9')      
    ax.add_feature(cfeature.BORDERS, edgecolor='0.4', linewidth=0.8)
    ax.add_feature(cfeature.STATES, edgecolor='0.2', linewidth=0.2)
    if coastline == True:
        ax.add_feature(cfeature.COASTLINE, edgecolor='0.4', linewidth=0.8)
    if mask_ocean == True:
        ax.add_feature(cfeature.OCEAN, edgecolor='0.4', zorder=12, facecolor='white') # mask ocean
        
    ## Tickmarks/Labels
    ## Add in meridian and parallels
    if mapcrs == ccrs.NorthPolarStereo(central_longitude=0.):
        gl = ax.gridlines(draw_labels=False,
                      linewidth=.5, color='black', alpha=0.5, linestyle='--')
    elif mapcrs == ccrs.SouthPolarStereo(central_longitude=0.):
        gl = ax.gridlines(draw_labels=True,
                      linewidth=.5, color='black', alpha=0.5, linestyle='--')
        
    else:
        gl = ax.gridlines(crs=datacrs, draw_labels=True, **kw_grid)
        gl.top_labels = False
        gl.left_labels = left_lats
        gl.right_labels = right_lats
        gl.bottom_labels = bottom_lons
        gl.xlocator = mticker.FixedLocator(xticks)
        gl.ylocator = mticker.FixedLocator(yticks)
        gl.xformatter = LONGITUDE_FORMATTER
        gl.yformatter = LATITUDE_FORMATTER
        gl.xlabel_style = kw_ticklabels
        gl.ylabel_style = kw_ticklabels
        
        # apply tick parameters
        ax.set_xticks(xticks, crs=datacrs)
        ax.set_yticks(yticks, crs=datacrs)
        plt.yticks(color='w', size=1) # hack: make the ytick labels white so the ticks show up but not the labels
        plt.xticks(color='w', size=1) # hack: make the ytick labels white so the ticks show up but not the labels
        ax.ticklabel_format(axis='both', style='plain')
    
    ## Gridlines
    # Draw gridlines if requested
    if (grid == True):
        gl.xlines = True
        gl.ylines = True
    if (grid == False):
        gl.xlines = False
        gl.ylines = False

    ## Map Extent
    # If no extent is given, use global extent
    if extent is None:        
        ax.set_global()
        extent = [-180., 180., -90., 90.]
    # If extent is given, set map extent to lat/lon bounding box
    else:
        ax.set_extent(extent, crs=datacrs)
    
    return ax


def plot_time_height_meteograms(ds, varname, lat, lon, model_name, duration):
    '''
    Plots WVFlux Meteogram Plot from given data
    
    Parameters
    ----------
    ds : 
        xarray object
        
    varname : str
        str that is either wvflux or r
        
    lat : str
        latitude point to run the plots on
        
    lon : str
        longitude point to run the plots on
        
    model_name : str
        ECMWF or GFS
    
    duration : int
        duration of plot - either 7 or 3 (day)
  
    Returns
    -------
    png : 
        time-height Meteogram figure
    
    '''
    if (duration == 7) & (model_name == 'ECMWF'):
        xtick_dur = 2
    elif (duration == 7) & (model_name == 'GFS'):
        xtick_dur = 4
    else:
        xtick_dur = 2
    
    if model_name == 'GFS':
        ds = ds.transpose('isobaricInhPa', 'step')
        xs2 = ds.valid_time.values
        ys = ds.isobaricInhPa.values
    elif model_name == 'ECMWF':
        ds = ds.transpose('hybrid', 'step')
        xs2 = ds.valid_time_td.values
        ys = ds.pressure.values
    else:
        print('Choose either GFS or ECMWF', flush=True)
        
    kw_ticks = {'length': 4, 'width': 0.5, 'pad': 2, 'color': 'black',
                'labelsize': 10, 'labelcolor': 'dimgray'}

    kw_ticklabels = {'size': 8, 'color': 'dimgray', 'weight': 'light'}
    style = {'size': 10, 'color': 'black', 'fontweight': 'normal'}

    ## create title label
    clon = ((lon + 180) % 360) - 180
    if clon > 0:
        lon_lbl = u"{:.0f}\N{DEGREE SIGN}E".format(clon)
        flon_lbl = u"{:.0f}E".format(clon)
    else:
        lon_lbl = u"{:.0f}\N{DEGREE SIGN}W".format(clon*-1)
        flon_lbl = u"{:.0f}W".format(clon*-1)
    
    lat_lbl = u"{:.0f}\N{DEGREE SIGN}N".format(lat)
    flat_lbl = u"{:.0f}N".format(lat)
    wvflux_units = 'kg m$^{-2}$ s$^{-1}$'
    ivt_units = 'kg m$^{-1}$ s$^{-1}$'
    rh_units = '%'
    wind_units = '(knots)'
    title = '{0} {1}-day Time-Height Meteogram | {2} {3}'.format(model_name, duration, lat_lbl, lon_lbl)

    init_date = pd.to_datetime(ds.time.values).strftime('%H UTC %d %b %Y')
    left_title = 'Initialized: {0}'.format(init_date)
    
    ### Get x-tick and x-labels for both cases
    x1 = ds.valid_time.values

    x_lst = [x1]
    xlbl_lst = []
    xtick_lst = []
    for i, x in enumerate(x_lst):
        x_lbl = []
        xtick_lst.append(x)
        for j in range(len(x)):
            t = pd.to_datetime(str(x[j]))
            x_lbl.append(t.strftime('%d/%H'))
            xlbl_lst.append(x_lbl)
    
    ## find where IVT >=250 and IWV >=20 for shading
    idx = (ds.ivt >=250) & (ds.pwat >=20.)
    s = pd.Series(xr.where(idx, True, False))
    grp = s.eq(False).cumsum()
    arr = grp.loc[s.eq(True)] \
             .groupby(grp) \
             .apply(lambda x: [x.index.min(), x.index.max()])

    current_dpi=300
    base_dpi=100
    scaling_factor = (current_dpi / base_dpi)**0.2

    set_cw3e_font(current_dpi, scaling_factor)

    nrows = 4
    ncols = 1

    ## Use gridspec to set up a plot with a series of subplots that is
    ## n-rows by n-columns
    gs = GridSpec(nrows, ncols, height_ratios=[2, 0.05, 1, 1], width_ratios = [1], wspace=0.06, hspace=0.1)
    ## use gs[rows index, columns index] to access grids
    fig = plt.figure(figsize=(10., 14.))
    fig.dpi = current_dpi
    fig_path = '/data/projects/operations/wvflux_meteograms/figs/'
    if varname == 'wvflux':
        fname = fig_path + '{0}/{0}_{1}DayWVFlux_{2}_{3}'.format(model_name, duration, flat_lbl, flon_lbl)
    elif varname == 'r':
        fname = fig_path + '{0}/{0}_{1}DayRH_{2}_{3}'.format(model_name, duration, flat_lbl, flon_lbl)
    else:
        print('please choose either r or wvflux for varname', flush=True)
        
    
    fmt = 'png'

    ####################
    ### TIME-HEIGHT  ###
    ####################
    ax = fig.add_subplot(gs[0, 0])
    ## y-axis is pressure
    ## x-axis is time
    xs = ds.valid_time.values
    terline = ds.sp.values / 100. ## convert from Pa to hPa
    ht_fill = ax.fill_between(xs, 1000., terline, facecolor='k', edgecolor='k', zorder=10)

    # Filled contours
    
    cmap, norm, bnds, cbarticks, cbarlbl = ccmaps.cmap(varname) # get cmap from our custom function
    ## filled contours
    cf = ax.contourf(xs2, ys, ds[varname].values, levels=bnds, cmap=cmap, norm=norm, alpha=1, extend='neither', zorder=-1)
    ## contour lines
    cs = ax.contour(xs2, ys, ds[varname].values, levels=bnds, colors=['grey'], linewidths=0.3, alpha=1, zorder=9)

    if varname == 'wvflux':
        ylbl = u"WV Flux ({0}) | UV (knots) | T (0\N{DEGREE SIGN}C) | Pressure (hPa)".format(wvflux_units)
    elif varname == 'r':
        ylbl = u"RH ({0}) | UV (knots) | T (0\N{DEGREE SIGN}C) | Pressure (hPa)".format(rh_units)
    else:
        print('please choose either r or wvflux for varname', flush=True)
    
    plt.gca().invert_yaxis()
    ax.yaxis.set_label_position("left")
    ax.yaxis.tick_left()
    ax.set_ylabel(ylbl)
    ax.set_ylim(1000, 200)
    ax.set_yticks([1000., 850., 700., 500., 400., 300., 250., 200.])

    ## add freezing level
    kw_clabels = {'fontsize': 11, 'inline': True, 'inline_spacing': 5, 'fmt': '%i',
                  'rightside_up': True, 'use_clabeltext': True}
    z0 = ax.contour(xs2, ys, ds['t'].values-273.15, levels=[0], colors=['k'], linewidths=1.25, alpha=1, zorder=100)
    plt.clabel(z0, **kw_clabels)

    # wind vectors
    if model_name == 'ECMWF':
        dw = 4 # how often to plot vector vertically
        dw2 = 1 # how often to plot horizontally
        ax.barbs(xs2[::dw, ::dw2], ys[::dw, ::dw2], 
                 ds.u.values[::dw, ::dw2]*1.94384, ds.v.values[::dw, ::dw2]*1.94384, 
                 linewidth=0.75, length=5.5)
    elif model_name == 'GFS':
        dw = 2 # how often to plot vector
        ax.barbs(xs2[::dw], ys[::dw], 
                 ds.u.values[::dw, ::dw]*1.944, ds.v.values[::dw, ::dw]*1.944, 
                 linewidth=0.75, length=5.5)
    else:
        print('Choose either GFS or ECMWF', flush=True)

    ## apply xtick parameters (day/hour)
    x_ticks = xtick_lst[0]
    x_labels = xlbl_lst[0]
    ax.set_xticks(x_ticks[::xtick_dur]) # set the labels every x time steps
    ax.set_xticklabels(x_labels[::xtick_dur])

    ## add titles
    # ax.set_title(right_title, loc="right")
    ax.set_title(title + "\n" + left_title, loc="left")

    # # Add color bar
    cbax = fig.add_subplot(gs[1, 0]) # colorbar axis
    cb = Colorbar(ax = cbax, mappable = cf, orientation = 'horizontal', ticklocation = 'bottom', ticks=cbarticks)
    # cb.ax.tick_params(labelsize=12)
    cb.ax.set_xticklabels(['{:g}'.format(x) for x in cbarticks]) # force cbartick labels to drop trailing zeros

    ## Add CW3E logo
    in_ax = inset_axes(ax, width="10%", height="20%", loc='upper left')
    in_ax = plot_cw3e_logo(in_ax, orientation='vertical')

    ########################
    ### PREC TIME SERIES ###
    ########################
    ax = fig.add_subplot(gs[2, 0])
    width = xs[1] - xs[0]
    prec_colors = xr.where(ds.gh < (ds.orog), x='#4876FF', y='#04FF03').values
    z0_mask = xr.where(ds.gh < (ds.orog), x=True, y=False).values
    prec = ax.bar(xs, height=ds.tp.values, width=width*-1, edgecolor='grey',
                  color=prec_colors, alpha=1, align='edge')
    if duration == 3:
        ax.set_ylabel('3-hr Precip (mm)', color='k')
    elif duration == 7:
        ax.set_ylabel('6-hr Precip (mm)', color='k')
    else:
        print('Choose either 3 or 7 for duration', flush=True)

    ax2 = ax.twinx()  # instantiate a second axes that shares the same x-axis
    ax2.plot(xs, ds.gh.values, color='#4876FF', linewidth=0.75)
    ax2.plot(xs, ds.gh.where(ds.gh >= (ds.orog)).values, color='#04FF03', linewidth=0.75)
    ax2.set_ylabel(u'Height of 0\N{DEGREE SIGN}C Isotherm (gpm)', color='k', rotation=270, labelpad=15)
    ax2.axhline(y=ds.orog.values[0], color='k', linestyle='--')
    ax2.set_xlim(xs[0], xs[-1])
    
    ## apply xtick parameters (day/hour)
    x_ticks = xtick_lst[0]
    x_labels = xlbl_lst[0]
    ax.set_xticks(x_ticks[::xtick_dur]) # set the labels every x time steps
    ax.set_xticklabels(x_labels[::xtick_dur])
    # Set the minor ticks every 3 hours
    ax.xaxis.set_minor_locator(HourLocator(range(0, 25, 3)))
    ax.tick_params(axis='x', which='minor', bottom=True)
    ax.tick_params(axis='x', which='major')

    if np.nanmax(ds.tp.values) < 5:
        yticks = np.arange(0, 5, 1)
        ax.yaxis.set_major_locator(mticker.FixedLocator(yticks))
        ax.tick_params(axis='y', which='minor', left=True)
        ax.set_ylim(0, 5) 
    else:
        # Set a maximum of 5 ticks on the y-axis
        ax.yaxis.set_major_locator(MaxNLocator(5))
        ax.minorticks_on()
        ax.tick_params(axis='y', which='minor', left=True)
        ax.set_ylim(bottom=0)
    
    # Set a maximum of 5 ticks on the y-axis
    ax2.yaxis.set_major_locator(MaxNLocator(5))
    ax2.xaxis.set_minor_locator(HourLocator(range(0, 25, 3)))
    ax2.tick_params(axis='y', which='minor', right=True)
    ax2.set_ylim(bottom=0)
    
    prec_sum = np.nansum(ds.tp.values)
    prec_ann = 'Total Precip = {0:0.2f} mm'.format(prec_sum)
    if prec_sum < 100:
        xl = .80
    else:
        xl = .78
    ax.annotate(prec_ann, # this is the text
                (xl, .91), # these are the coordinates to position the label
                xycoords='axes fraction',
                zorder=200,
                **style)
    
    #######################
    ### IVT TIME SERIES ###
    #######################
    ax = fig.add_subplot(gs[3, 0])

    ax.plot(xs, ds.pwat.values, color='blue', linewidth=0.75)
    ax.set_ylabel('IWV (mm)', color='blue')
    ax.axhline(y=20.0, color='blue', linestyle='--', linewidth=0.75)
    ax.set_xlim(xs[0], xs[-1])
    
    if np.nanmax(ds.pwat.values) < 30:
        yticks = np.arange(0, 30, 5)
        ax.yaxis.set_major_locator(mticker.FixedLocator(yticks))
        ax.tick_params(axis='y', which='minor', left=True)
        ax.set_ylim(0, 30)
    else:
        # Set a maximum of 5 ticks on the y-axis
        ax.yaxis.set_major_locator(MaxNLocator(5))
        ax.minorticks_on()
        ax.tick_params(axis='y', which='minor', left=True)
        ax.set_ylim(bottom=0)

    ax2 = ax.twinx()  # instantiate a second axes that shares the same x-axis
    ax2.plot(xs, ds.ivt.values, color='red')
    ax2.set_ylabel('IVT (kg m$^{-1}$ s$^{-1}$)', color='red', rotation=270, labelpad=15)
    ax2.axhline(y=250.0, color='red', linestyle='--')
    ax2.set_xlim(xs[0], xs[-1])
    
    if np.nanmax(ds.ivt.values) < 300:
        yticks = np.arange(0, 300, 50)
        ax2.yaxis.set_major_locator(mticker.FixedLocator(yticks))
        ax2.tick_params(axis='y', which='minor', left=True)
        ax2.set_ylim(0, 300)
    else:
        # Set a maximum of 5 ticks on the y-axis
        ax2.yaxis.set_major_locator(MaxNLocator(5))
        ax2.minorticks_on()
        ax2.tick_params(axis='y', which='minor', right=True)
        ax2.set_ylim(bottom=0)
    
    ## apply xtick parameters (day/hour)
    x_ticks = xtick_lst[0]
    x_labels = xlbl_lst[0]
    ax.set_xticks(x_ticks[::xtick_dur]) # set the labels every x time steps
    ax.set_xticklabels(x_labels[::xtick_dur])
    # Set the minor ticks using FixedLocator
    ax.xaxis.set_minor_locator(HourLocator(range(0, 25, 3)))  
    # ax.xaxis.set_minor_locator(ticker.FixedLocator(x_ticks))
    # ax.minorticks_on()
    ax.tick_params(axis='x', which='minor', bottom=True)
    ax.tick_params(axis='x', which='major')

    ## add in grey shading where IWV and IVT > thres
    # shade +/- 1.5 hours from the valid time of AR conditions
    AR_duration = []
    prec_AR = []
    for i in range(len(arr)):
        if duration == 3:
            start = xs[arr.iloc[i][0]] - np.timedelta64(5400, 's')
            stop = xs[arr.iloc[i][1]] + np.timedelta64(5400, 's')
        else:
            start = xs[arr.iloc[i][0]] - np.timedelta64(21600, 's')
            stop = xs[arr.iloc[i][1]] + np.timedelta64(21600, 's')
        AR_dur = (stop - start) / np.timedelta64(1, 'h')
        AR_duration.append(AR_dur)
        midway = (AR_dur / 2) + start
        ax.axvspan(start, stop, color='grey', alpha=0.2, lw=None)
        
        ## sum up precipitation during AR conditions
        prec = ds.tp.isel(step=slice(arr.iloc[i][0]-1, arr.iloc[i][1]+1)).values
        prec = np.nansum(prec)
        if (prec > 1) & (AR_dur > 6):
            prec_ann = 'Precip = {0:0.1f} mm'.format(prec)
            ## plot precipitation annotation when there are AR events
            ax.annotate(prec_ann, # this is the text
                        (midway, 0.03), # these are the coordinates to position the label
                        xycoords='data',
                        ha='center',
                        zorder=200,
                        **style)
        
    AR_duration = sum(AR_duration)
    # prec_AR = sum(prec_AR) ## instead of summing, keep as individual events

    ## add in annotation of max IWV and IVT vals
    IVT_IWV_ann = 'Max IVT/IWV = {0:0.0f} {1} / {2:0.0f} mm'.format(ds.ivt.max().values, ivt_units, ds.pwat.max().values)
    AR_ann = 'AR Conditions = {0} hours'.format(int(AR_duration))
    
    
    if ds.ivt.max().values >= 1000:
        xy1 = .77
    else:
        xy1 = .78
    xy = [(.01, .91), (xy1, .91)]
    for i, lbl in enumerate([IVT_IWV_ann, AR_ann]):
        ax.annotate(lbl, # this is the text
                    xy[i], # these are the coordinates to position the label
                    xycoords='axes fraction',
                    zorder=200,
                    **style)

    fig.savefig('%s.%s' %(fname, fmt), bbox_inches='tight', dpi=fig.dpi, transparent=False)
    # fig.clf()
    # close figure
    plt.close(plt.gcf())
