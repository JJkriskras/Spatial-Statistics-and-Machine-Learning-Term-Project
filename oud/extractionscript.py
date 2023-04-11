# Import packages
import osgeo
from os.path import join as pjoin
import pandas as pd
import numpy as np
import xarray as xr
import xrspatial as xrs
import rioxarray

import os
os.environ['USE_PYGEOS'] = '0'
import geopandas as gpd
import matplotlib.pyplot as plt
import seaborn as sns

import pystac
from pystac_client import Client
import pystac.item_collection as pyic
import planetary_computer
import requests
import stackstac

import rich.table
import dask.diagnostics

scratch_dir = './Project/scratch' 

from pystac_client import Client
import planetary_computer as pc

#--------------------------------------------------------------------------------

def importdata(aoi, daterange):
    catalog = Client.open(
        "https://planetarycomputer.microsoft.com/api/stac/v1"
        )
    # Define your search with CQL2 syntax
    search = catalog.search(filter_lang="cql2-json", filter={
        "op": "and",
        "args": [{"op": "s_intersects", "args": [{"property": "geometry"}, aoi]},
                {"op": "anyinteracts", "args": [{"property": "datetime"}, daterange[0]]},
                {"op": "=", "args": [{"property": "collection"}, "landsat-c2-l2"]},
                {"op": "<=", "args": [{"property": "eo:cloud_cover"}, 20]}
                ]
        }
    )


    first_item = next(search.get_items())
    pc.sign_item(first_item).assets

    charts = search.get_all_items()
    print(daterange[0],len(charts))
               
        #########################
    for t in daterange[1:]:
         # Search against the Planetary Computer STAC API
        catalog = Client.open(
            "https://planetarycomputer.microsoft.com/api/stac/v1")
        # Define your search with CQL2 syntax
        search = catalog.search(filter_lang="cql2-json", filter={
            "op": "and",
                "args": [
                    {"op": "s_intersects", "args": [{"property": "geometry"}, aoi]},
                    {"op": "anyinteracts", "args": [{"property": "datetime"}, t]},
                    {"op": "=", "args": [{"property": "collection"}, "landsat-c2-l2"]},
                    # data cant process more than k-amount of bands so cloud coverage can be set to almost 0
                    {"op": "<=", "args": [{"property": "eo:cloud_cover"}, 20]} 
                ]
            }  
        )

        first_item = next(search.get_items())
        pc.sign_item(first_item).assets

        items = search.get_all_items()
        print(t,'items: ',len(items))
        charts = charts+items
        

    print('Length total item set:',len(charts)) 
    return charts 

#-------------------------------------------------------------------------
#------------------------------------------------------------------------
#-------------------------------------------------------------------------



# Define your area of interest
aoi_BMV = { #aoi Everest and Makalu Valley Polygon
  "type": "Polygon",
  "coordinates": [
    [
        [86.704525, 27.552301],
        [87.181495, 27.970180],
        [87.276902, 27.567789],
        [86.704525, 27.567789],
        [86.704525, 27.552301]
    ]
  ]
}


daterange = [
    {"interval": ["1992-08-01T00:00:00Z", "1993-11-01T00:00:00Z"]},
    {"interval": ["1995-08-01T00:00:00Z", "1995-11-01T00:00:00Z"]},
    {"interval": ["1998-08-01T00:00:00Z", "1998-11-01T00:00:00Z"]},
    {"interval": ["2001-08-01T00:00:00Z", "2001-11-01T00:00:00Z"]},
    {"interval": ["2004-08-01T00:00:00Z", "2004-11-01T00:00:00Z"]},
    {"interval": ["2007-08-01T00:00:00Z", "2007-11-01T00:00:00Z"]},
    {"interval": ["2010-08-01T00:00:00Z", "2010-11-01T00:00:00Z"]},
    {"interval": ["2013-08-01T00:00:00Z", "2013-11-01T00:00:00Z"]},
    {"interval": ["2016-08-01T00:00:00Z", "2016-11-01T00:00:00Z"]},
    {"interval": ["2019-08-01T00:00:00Z", "2019-11-01T00:00:00Z"]},
    {"interval": ["2022-08-01T00:00:00Z", "2022-11-01T00:00:00Z"]}
]

charts = importdata(aoi_BMV, daterange)

ds = stackstac.stack(planetary_computer.sign(charts), epsg=6207)

with dask.diagnostics.ProgressBar():
    ts = ds.compute()

ts.rio.to_raster(pjoin(scratch_dir, 'ts.tif'), compress='LZW')