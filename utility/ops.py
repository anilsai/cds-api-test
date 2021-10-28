import pandas as pd
import logging
import cdsapi
import xarray as xr
from urllib.request import urlopen
import plotly
import json
import os
import plotly.express as px

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
cds_client = cdsapi.Client()


def call_api_fetch_data(req_parms):
    dataset = "reanalysis-era5-single-levels"
    fl = cds_client.retrieve(dataset, req_parms)
    # load into memory
    with urlopen(fl.location) as f:
        ds = xr.open_dataset(f.read())

    df_data = ds.to_dataframe()
    df_data['lat'] = df_data.index.get_level_values(0)
    df_data['long'] = df_data.index.get_level_values(1)
    df_data['time_stamp'] = df_data.index.get_level_values(2)
    df_data['time_str'] = df_data['time_stamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
    df_data[['date', 'time']] = df_data['time_str'].str.split(' ', expand=True)
    time_series = df_data[['time_stamp', 'tcc']]
    time_series.reset_index(drop=True, inplace=True)
    return df_data, time_series


def create_plot(data_df):
    figure = px.line(data_df, x='time_stamp', y='tcc')
    plot_json = json.dumps(figure, cls=plotly.utils.PlotlyJSONEncoder)
    return plot_json


def create_parms_month(year, month, lat, long):
    req_parms = {
        "format": "netcdf",
        "product_type": "reanalysis",
        "variable": "total_cloud_cover",
        'year': [year],
        'month': [month],
        'day': list(map("{:02d}".format, range(1, 31))),
        "time": ['00:00', '01:00', '02:00', '03:00', '04:00', '05:00', '06:00', '07:00', '08:00', '09:00', '10:00',
                 '11:00', '12:00',
                 '13:00', '14:00', '15:00', '16:00', '17:00', '18:00', '19:00', '20:00', '21:00', '22:00', '23:00'],
        "area": [long, lat, long, lat],
    }
    return req_parms


def create_parms_day(year, month, day, lat, long):
    req_parms = {
        "format": "netcdf",
        "product_type": "reanalysis",
        "variable": "total_cloud_cover",
        'year': [year],
        'month': [month],
        'day': [day],
        "time": ['00:00', '01:00', '02:00', '03:00', '04:00', '05:00', '06:00', '07:00', '08:00', '09:00', '10:00',
                 '11:00', '12:00',
                 '13:00', '14:00', '15:00', '16:00', '17:00', '18:00', '19:00', '20:00', '21:00', '22:00', '23:00'],
        "area": [long, lat, long, lat],
    }
    return req_parms


def select_object(date):
    with open(f'data/{date}.nc', 'rb') as f:
        ds = xr.open_dataset(f.read())
    data_df = process_xarray_to_df(ds)
    return data_df


def filter_df_lat_long(data_df, lat, long):
    data_df = data_df.loc[data_df['long'] == float(lat)]
    data_df = data_df.loc[data_df['lat'] == float(long)]
    time_series = data_df[['time_stamp', 'tcc']]
    time_series.reset_index(drop=True, inplace=True)

    return data_df, time_series


def select_filter_monthly_objects(date, lat, long):
    contents = os.listdir("data/")
    month_df = pd.DataFrame()
    for i in contents:
        try:
            with open(f'data/{i}', 'rb') as f:
                ds = xr.open_dataset(f.read())
            data_df_day = process_xarray_to_df(ds)
            data_df_day = data_df_day.loc[data_df_day['long'] == float(lat)]
            data_df_day = data_df_day.loc[data_df_day['lat'] == float(long)]
            month_df = month_df.append(data_df_day)
            logger.info(f'processed {i}')
        except Exception as e:
            print(i)
            print(e)

    return month_df


def process_xarray_to_df(xarry_frame):
    data_df = xarry_frame.to_dataframe()
    data_df['lat'] = data_df.index.get_level_values(0)
    data_df['long'] = data_df.index.get_level_values(1)
    data_df['time_stamp'] = data_df.index.get_level_values(2)
    data_df['time_str'] = data_df['time_stamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
    data_df[['date', 'time']] = data_df['time_str'].str.split(' ', expand=True)
    return data_df
