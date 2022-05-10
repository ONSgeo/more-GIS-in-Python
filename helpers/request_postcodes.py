"""
Module with utility functions to help with More GIS in Python Course

This module may require the following to work:

!pip install python-certifi-win32 requests
"""
import geopandas as gpd
import json
import numpy as np
import os
import pandas as pd
from pathlib import Path
import requests
from requests.auth import HTTPProxyAuth
import urllib


POSTCODE_FIELDS = ['geometry', 'objectid', 'pcd', 'pcd2', 'pcds', 'dointr',
                   'doterm', 'oscty', 'ced', 'oslaua', 'osward', 'usertype',
                   'oseast1m', 'osnrth1m', 'osgrdind', 'oshlthau', 'nhser', 'ctry', 'rgn', 'pcon', 'eer', 'ttwa', 'itl', 'park', 'oa11', 'lsoa11', 'msoa11', 'parish', 'wz11', 'ccg', 'bua11', 'buasd11', 'ru11ind', 'oac11', 'lat', 'long', 'lep1', 'lep2',   'pfa', 'imd', 'calncv', 'stp', 'pcdn']



def request_postcodes_from_list(pcds_list, outfile=None, fields='all'):
    """Function to request postcode tables and geometry from ONS Geoportal @ https://ons-inspire.esriuk.com/arcgis/rest/services/Postcodes/ONSPD_Centroids_Lite/FeatureServer/0/ endpoint

    Parameters
    -----------
    pcds_list : (list)
        List of postcodes to request

    outfile : (None/Path/str)
        Option to save response as shapefile/geopackage. (DEFAULT = None)

    fields : (str/list)
        If left as default, all fields will be requested, else those in the
        list from ['geometry', 'objectid', 'pcd', 'pcd2', 'pcds', 'dointr',
        'doterm',
       'oscty', 'ced', 'oslaua', 'osward', 'usertype', 'oseast1m', 'osnrth1m',
       'osgrdind', 'oshlthau', 'nhser', 'ctry', 'rgn', 'pcon', 'eer', 'ttwa',
       'itl', 'park', 'oa11', 'lsoa11', 'msoa11', 'parish', 'wz11', 'ccg',
       'bua11', 'buasd11', 'ru11ind', 'oac11', 'lat', 'long', 'lep1', 'lep2',
       'pfa', 'imd', 'calncv', 'stp', 'pcdn']. NOTE THAT NOT INCLUDING
       GEOMETRY RESULT IN REGULAR DATAFRAME BEING CREATED WITOUT GEOMETRY.
    """
    os.environ['http_proxy'] = "http://10.173.135.52:8080"
    os.environ['https_proxy'] = "http://10.173.135.52:8080"


    session = requests.Session()
    session.trust_env = False
    URL = "https://ons-inspire.esriuk.com/arcgis/rest/services/Postcodes/ONSPD_Centroids_Lite/FeatureServer/0/query?"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0",
        "Accept-Encoding": "*",
        "Connection": "keep-alive"
    }

    pcds = tuple(set(list(pcds_list)))

    if fields == 'all':
        out_fields = "*"
    else:
        try:
            assert set(fields).issubset(POSTCODE_FIELDS)
            out_fields = ', '.join(fields)
        except AssertionError as e:
            raise Exception(f"Please use list of valid fields as outfields from list: {POSTCODE_FIELDS}")
    params = {
    'where': f"pcds in {pcds}",
    'outFields': out_fields,
    'f': 'geojson'
    }
    url = URL + urllib.parse.urlencode(params)
    r = session.get(url=url, headers=headers)
    data = r.json()
    gdf = gpd.GeoDataFrame.from_features(data, crs=4236)
    if outfile:
        try:
            gdf.to_file(outfile, index=False)
        except Exception as e:
            raise Exception("Please use a valid .gpkg or .shp path for outfile")
    return gdf






if __name__ == "__main__":
    BASE = Path(__file__).resolve().parent.parent
    CSV = BASE.joinpath(
        "data/csv/london_fire_brigade_stations.csv")
    outfile = CSV.parent.joinpath("stations_locations.shp")
    stations = pd.read_csv(CSV)
    stations['postcode'] = stations['Address'].str.rsplit(', ').str[-1]
    pcds = stations.postcode
    gdf = request_postcodes_from_list(pcds, outfile=outfile, fields=[
        "geometry", "pcds", "parish"])

