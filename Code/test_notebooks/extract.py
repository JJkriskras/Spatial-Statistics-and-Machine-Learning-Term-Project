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
import stackstac
import dask.diagnostics
scratch_dir = './data' 
import planetary_computer as pc


format = int(input('What format should be extracted? type 1 for NDSI, 2 for NDWI, 3 for NDGI:\n'))

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
                    {"op": "<=", "args": [{"property": "eo:cloud_cover"}, 20]} 
                ]
            }  
        )

        first_item = next(search.get_items())
        pc.sign_item(first_item).assets

        items = search.get_all_items()
        print(t,'items: ',len(items))
        charts += items
        

    print('Length total item set:',len(charts)) 
    return charts    

#--------------------------------------------------------------------------
#--------------------------------------------------------------------------
def create_file(ds, format, datause = ''):
    if format == 1:
        green = ds.sel(band = 'green')
        swir = ds.sel(band = 'swir16')
        NDSI = (green - swir) / (green + swir)
        resampledNDSI = NDSI.resample(time="YS")\
            .mean("time", keep_attrs=True) # the most frequent value
        
        with dask.diagnostics.ProgressBar():
            ts = resampledNDSI.compute()

        ts.rio.to_raster(pjoin(scratch_dir,datause+'resampledNDSI.tif'), compress='LZW')
        print('NDSI done')
    #---------------------------------------------
    elif format == 2:
        green = ds.sel(band = 'green')
        nir = ds.sel(band = 'nir08')
        NDWI = (green - nir) / (green + nir)
        resampledNDWI = NDWI.resample(time="YS")\
            .mean("time", keep_attrs=True) # the most frequent value
        
        with dask.diagnostics.ProgressBar():
            ts = resampledNDWI.compute()

        ts.rio.to_raster(pjoin(scratch_dir, datause+'resampledNDWI.tif'), compress='LZW')
        print('NDWI done')     
    #---------------------------------------------   
    elif format == 3:
        green = ds.sel(band = 'green')
        red = ds.sel(band = 'red')
        NDGI = (green - red) / (green + red)
        resampledNDGI = NDGI.resample(time="YS")\
            .mean("time", keep_attrs=True) # the most frequent value
        
        with dask.diagnostics.ProgressBar():
            ts = resampledNDGI.compute()

        ts.rio.to_raster(pjoin(scratch_dir,datause + 'resampledNDGI.tif'), compress='LZW')
        print('NDGI done') 
    else: pass
#-------------------------------------------------------------------------
#------------------------------------------------------------------------
#--------------------------------------------------------------------------
#--------------------------------------------------------------------------
# Define your area of interest
aoi_BMV = { #aoi Everest and Barun/Makalu national park polygon
  "type": "Polygon",
  "coordinates": [
    [
        [86.736074, 28.136264],
        [87.181495, 27.970180],
        [87.276902, 27.567789],
        [87.276902, 28.136264],
        [86.736074, 28.136264]
    ]
  ]
}
#------------------------------------------------------
daterange = [
    #{"interval": ["1983-09-01T00:00:00Z", "1983-11-01T00:00:00Z"]}, no data
    #{"interval": ["1986-09-01T00:00:00Z", "1986-11-01T00:00:00Z"]}, no data
    #{"interval": ["1989-08-01T00:00:00Z", "1989-11-01T00:00:00Z"]}, no data
    {"interval": ["1992-09-01T00:00:00Z", "1992-11-01T00:00:00Z"]}, # 1
    {"interval": ["1995-09-01T00:00:00Z", "1995-11-01T00:00:00Z"]}, # 2
    {"interval": ["1998-09-01T00:00:00Z", "1998-11-01T00:00:00Z"]}, # 3
    {"interval": ["2001-09-01T00:00:00Z", "2001-11-01T00:00:00Z"]}, # 4
    {"interval": ["2004-09-01T00:00:00Z", "2004-11-01T00:00:00Z"]}, # 5
    {"interval": ["2007-09-01T00:00:00Z", "2007-11-01T00:00:00Z"]}, # 6
    {"interval": ["2010-09-01T00:00:00Z", "2010-11-01T00:00:00Z"]}, # 7
    {"interval": ["2013-09-01T00:00:00Z", "2013-11-01T00:00:00Z"]}, # 8
    {"interval": ["2016-09-01T00:00:00Z", "2016-11-01T00:00:00Z"]}, # 9
    {"interval": ["2019-09-01T00:00:00Z", "2019-11-01T00:00:00Z"]}, # 10
    {"interval": ["2022-09-01T00:00:00Z", "2022-11-01T00:00:00Z"]}, # 11
    {"interval": ["2009-09-01T00:00:00Z", "2009-11-01T00:00:00Z"]}, # train
    {"interval": ["1999-09-01T00:00:00Z", "1999-11-01T00:00:00Z"]} # validation
]
#--------------------------------------------------------
charts = importdata(aoi_BMV, daterange)

traincheck,valcheck = 0, 0
r = []
for i, c in zip(charts, range(len(charts))):
    if i.datetime.year == 2009:
        #print(i, c)
        if traincheck == 0:
            train = pystac.ItemCollection(items= [charts[c]])
            #print('done')
            traincheck += 1
        else:
            train += pystac.ItemCollection(items= [charts[c]])  
        #print('check')

        r.append(i)

    elif i.datetime.year == 1999:
        if valcheck == 0:
            val = pystac.ItemCollection(items= [charts[c]])
            valcheck += 1
        else:
            val += pystac.ItemCollection(items= [charts[c]])  

        r.append(i)

    else: continue

for rem in r:
    charts.items.remove(rem)
print(f'length train: {len(train)} \nlength val: {len(val)}\nlength charts: {len(charts)}')
#--------------------------------------------------------
ds = stackstac.stack(planetary_computer.sign(charts), epsg=6207)
dt = stackstac.stack(planetary_computer.sign(train), epsg=6207)
dv = stackstac.stack(planetary_computer.sign(val), epsg=6207)

# Set to a small area in espg 6207 to limit computation time.
xmin, xmax, ymin, ymax = 86.441784772,87.420108894,26.867723927,28.196017654 
ds = ds.loc[:,:, ymax:ymin,xmin:xmax]
dt = dt.loc[:,:, ymax:ymin,xmin:xmax]
dv = dv.loc[:,:, ymax:ymin,xmin:xmax]
#----------------------------------------------------------
create_file(ds = ds, format = format)
print('charts done')
create_file(ds = dt, format= format, datause='train_data_')
print('train done')
create_file(ds = dv, format= format, datause='validation_data_')
print('val done')