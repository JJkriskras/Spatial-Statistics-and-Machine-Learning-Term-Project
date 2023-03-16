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

######################################################

# Define your area of interest Everest and Makalu
aoi_EMV = { #aoi Everest and Makalu Valley Polygon
  "type": "Polygon",
  "coordinates": [
    [
      [86.63380152490207, 28.56507505979343],
      [87.74001280776696, 28.479331576213163],
      [87.7789385926358, 28.213296130511523],
      [87.61479871540345, 27.906713498710847],
      [87.61479871540345, 27.906713498710847],
      [87.04816717665705, 27.239072299890207],
      [87.04816717665705, 27.239072299890207],
      [28.54835734379745, 86.06605505495027],
      [86.63380152490207, 28.56507505979343]
    ]
  ]
}

aoi_KV = { # aoi Kachenjunga Valley
"type": "Polygon",
  "coordinates": [
    [
    [86.63380152490207, 28.56507505979343],
    [87.74001280776696, 28.479331576213163],
    [87.7789385926358, 28.213296130511523],
    [87.61479871540345, 27.906713498710847],
    [87.61479871540345, 27.906713498710847],
    [87.15652306810863, 27.36778735019498],
    [89.06841422478996, 27.269554114998044],
    [89.06841422478996, 28.56507505979343],
    [86.63380152490207, 28.56507505979343]
    ]
  ]
}


#########################################################3
# 1984 only has 1 band, so date is increased
daterange = [
    {"interval": ["1985-09-01T00:00:00Z", "1985-11-01T00:00:00Z"]},
    {"interval": ["1990-09-01T00:00:00Z", "1990-11-01T00:00:00Z"]},
    {"interval": ["1995-09-01T00:00:00Z", "1995-11-01T00:00:00Z"]},
    {"interval": ["2000-09-01T00:00:00Z", "2000-11-01T00:00:00Z"]},
    {"interval": ["2005-09-01T00:00:00Z", "2005-11-01T00:00:00Z"]},
    {"interval": ["2010-09-01T00:00:00Z", "2010-11-01T00:00:00Z"]},
    {"interval": ["2015-09-01T00:00:00Z", "2015-11-01T00:00:00Z"]},
    {"interval": ["2020-09-01T00:00:00Z", "2020-11-01T00:00:00Z"]},
    {"interval": ["2022-09-01T00:00:00Z", "2022-11-01T00:00:00Z"]}]

def importdata(aoi, daterange):
    catalog = Client.open(
        "https://planetarycomputer.microsoft.com/api/stac/v1"
        )
    # Define your search with CQL2 syntax
    search = catalog.search(filter_lang="cql2-json", filter={
        "op": "and",
        "args": [{"op": "s_intersects", "args": [{"property": "geometry"}, aoi_EMV]},
                {"op": "anyinteracts", "args": [{"property": "datetime"}, daterange[0]]},
                {"op": "=", "args": [{"property": "collection"}, "landsat-c2-l2"]},
                {"op": "<=", "args": [{"property": "eo:cloud_cover"}, 2]}
                ]
        }
    )


    first_item = next(search.get_items())
    pc.sign_item(first_item).assets

    charts = search.get_all_items()
    print('1885 items:',len(charts))
               
        #########################
    for t in daterange[1:]:
         # Search against the Planetary Computer STAC API
        catalog = Client.open(
            "https://planetarycomputer.microsoft.com/api/stac/v1")
        # Define your search with CQL2 syntax
        search = catalog.search(filter_lang="cql2-json", filter={
            "op": "and",
                "args": [
                    {"op": "s_intersects", "args": [{"property": "geometry"}, aoi_EMV]},
                    {"op": "anyinteracts", "args": [{"property": "datetime"}, t]},
                    {"op": "=", "args": [{"property": "collection"}, "landsat-c2-l2"]},
                    # data cant process more than k-amount of bands so cloud coverage can be set to almost 0
                    {"op": "<=", "args": [{"property": "eo:cloud_cover"}, 2]} 
                ]
            }  
        )

        first_item = next(search.get_items())
        pc.sign_item(first_item).assets

        items = search.get_all_items()
        print(t,'items: ',len(items))
        charts = charts+items

    print('Length total item set:',len(charts))     

charts = importdata(aoi_EMV, daterange)


####################################################################3
ds = stackstac.stack(planetary_computer.sign(charts), epsg=6207) # Nepal coordinate system

##################################################################
# Compute
print('start computing')
with dask.diagnostics.ProgressBar():
    ts = ds.compute()

# save (uncomment)
#ts.rio.to_raster(pjoin(scratch_dir, 'ts.tif'), compress='LZW')
