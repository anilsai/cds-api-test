import os
import logging
import folium
import pandas as pd
from folium import plugins
from folium.plugins import HeatMap
from flask import request, url_for, render_template, redirect, make_response
from utility import FlaskLambda
from utility.ops import create_plot, create_parms_day, create_parms_month,\
    call_api_fetch_data, select_object, select_filter_monthly_objects, filter_df_lat_long
global final_df

final_df = pd.DataFrame()

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
lambda_handler = FlaskLambda(__name__)


@lambda_handler.route('/from_api/get_monthly_plot',methods=['GET'])
def get_data_for_month_api():
    date = request.args.get('date')
    year = date[2:6]
    month = date[:2]
    lat = request.args.get('lat')
    long = request.args.get('long')
    req_parms = create_parms_month(year, month, lat, long)
    data_df, time_df = call_api_fetch_data(req_parms)
    plot_json = create_plot(time_df)
    final_df = data_df
    return render_template('plot.html', graphJSON=plot_json, month=date, lat=lat, long= long, final_df=data_df)


@lambda_handler.route('/from_api/get_daily_plot', methods=['GET'])
def get_data_for_day_api():
    date = request.args.get('date')
    year = date[2:6]
    month = date[:2]
    day = date[2:4]
    lat = request.args.get('lat')
    long = request.args.get('long')
    req_parms = create_parms_day(year, month, day, lat, long)
    data_df, time_df = call_api_fetch_data(req_parms)
    plot_json = create_plot(time_df)
    final_df = data_df
    return render_template('plot.html', graphJSON=plot_json, month=date, lat=lat, long= long, final_df=data_df)


@lambda_handler.route('/from_api/daily_download_csv', methods=['GET'])
def download_data_for_day_api():
    date = request.args.get('date')
    year = date[2:6]
    month = date[:2]
    day = date[2:4]
    lat = request.args.get('lat')
    long = request.args.get('long')
    req_parms = create_parms_day(year, month, day, lat, long)
    data_df, time_df = call_api_fetch_data(req_parms)
    try:
        logger.info('downloading scores..')
        csv_resp = make_response(data_df.to_csv(index=False))
        logger.info(csv_resp)
        csv_resp.headers["Content-Disposition"] = "attachment; filename=" + "download.csv"
        csv_resp.headers["Content-Type"] = "text/csv"
        return csv_resp
    except Exception as e:
        logger.error(e)
        logger.info("has a problem with download")


@lambda_handler.route('/get/download_data', methods=['POST'])
def create_csv_month():
    try:
        logger.info('downloading scores..')
        csv_resp = make_response(final_df.to_csv(index=False))
        logger.info(csv_resp)
        csv_resp.headers["Content-Disposition"] = "attachment; filename=" + "download.csv"
        csv_resp.headers["Content-Type"] = "text/csv"
        return csv_resp
    except Exception as e:
        logger.error(e)
        logger.info("has a problem with download")


@lambda_handler.route('/from_api/get_daily_map',methods=['GET'])
def get_map_data_for_day_api():
    date = request.args.get('date')
    year = date[4:8]
    month = date[:2]
    day = date[2:4]
    lat = request.args.get('lat')
    long = request.args.get('long')
    req_parms = create_parms_day(year, month, day, lat, long)
    data_df, time_df = call_api_fetch_data(req_parms)
    tcc_max = format(data_df['tcc'].max(), '4f')
    tcc_min = format(data_df['tcc'].min(), '4f')
    tcc_avg = format(data_df['tcc'].mean(), '4f')
    start_coords = (lat, long)
    folium_map = folium.Map(location=start_coords, zoom_start=6)
    html = """
        <h1> Data for this location on {date}</h1><br>
        <p>
        <code>
            Avg TCC: {avg} <br>
            Max TCC: {max} <br>
            Min TCC: {min} <br>
        </code>
        </p>
        """.format(date=date, avg=tcc_avg, max=tcc_max, min=tcc_min)
    iframe = folium.IFrame(html=html, width=200, height=300)
    popup = folium.Popup(iframe, max_width=2650)

    folium.Marker([lat, long], popup=popup).add_to(folium_map)
    return folium_map._repr_html_()


@lambda_handler.route('/from_api/get_daily_json', methods=['GET'])
def get_data_data_json_api():
    date = request.args.get('date')
    year = date[4:8]
    month = date[:2]
    day = date[2:4]
    lat = request.args.get('lat')
    long = request.args.get('long')
    req_parms = create_parms_day(year, month, day, lat, long)
    data_df, time_df = call_api_fetch_data(req_parms)
    tcc_max = format(data_df['tcc'].max(), '4f')
    tcc_min = format(data_df['tcc'].min(), '4f')
    tcc_avg = format(data_df['tcc'].mean(), '4f')
    tcc_avg = format(data_df['tcc'].mean(), '4f')

    return_data = {
        'Latitude': lat,
        'Longitude': long,
        'TCC_max': tcc_max,
        'TCC_min': tcc_min,
        'TCC_mean': tcc_avg,
        'Date': date
    }
    return return_data


@lambda_handler.route('/from_file/get_daily_plot', methods=['GET'])
def get_daily_plot_from_file():
    date = request.args.get('date')
    lat = request.args.get('lat')
    long = request.args.get('long')
    data_df = select_object(date)
    filtered_df, time_df = filter_df_lat_long(data_df, lat, long)
    plot_json = create_plot(time_df)
    final_df = data_df
    return render_template('plot.html', graphJSON=plot_json, month=date, lat=lat, long=long, final_df=data_df)


@lambda_handler.route('/from_file/daily_download_csv', methods=['GET'])
def download_daily_csv_from_file():
    date = request.args.get('date')
    lat = request.args.get('lat')
    long = request.args.get('long')
    data_df = select_object(date)
    filtered_df, time_df = filter_df_lat_long(data_df, lat, long)
    try:
        logger.info('downloading scores..')
        csv_resp = make_response(filtered_df.to_csv(index=False))
        logger.info('created csv')
        csv_resp.headers["Content-Disposition"] = "attachment; filename=" + "download.csv"
        csv_resp.headers["Content-Type"] = "text/csv"
        return csv_resp
    except Exception as e:
        logger.error(e)
        logger.info("has a problem with download")


@lambda_handler.route('/from_file/get_monthly_plot', methods=['GET'])
def get_monthly_plot_from_file():
    date = request.args.get('date')
    lat = request.args.get('lat')
    long = request.args.get('long')
    data_df = select_filter_monthly_objects(date, lat, long)
    filtered_df, time_df = filter_df_lat_long(data_df, lat, long)
    plot_json = create_plot(time_df)
    final_df = data_df
    return render_template('plot.html', graphJSON=plot_json, month=date, lat=lat, long=long, final_df=data_df)


@lambda_handler.route('/from_file/get_monthly_json', methods=['GET'])
def get_monthly_json_from_file():
    date = request.args.get('date')
    lat = request.args.get('lat')
    long = request.args.get('long')
    data_df = select_filter_monthly_objects(date, lat, long)
    filtered_df, time_df = filter_df_lat_long(data_df, lat, long)
    tcc_max = format(filtered_df['tcc'].max(), '4f')
    tcc_min = format(filtered_df['tcc'].min(), '4f')
    tcc_avg = format(filtered_df['tcc'].mean(), '4f')

    return_data = {
        'Latitude': lat,
        'Longitude': long,
        'TCC_max': tcc_max,
        'TCC_min': tcc_min,
        'TCC_mean': tcc_avg,
        'Date': date
    }
    return return_data


@lambda_handler.route('/from_file/get_daily_map', methods=['GET'])
def get_data_map_for_day_file():
    date = request.args.get('date')
    lat = request.args.get('lat')
    long = request.args.get('long')
    data_df = select_object(date)
    filtered_df, time_df = filter_df_lat_long(data_df, lat, long)
    tcc_max = format(filtered_df['tcc'].max(), '4f')
    tcc_min = format(filtered_df['tcc'].min(), '4f')
    tcc_avg = format(filtered_df['tcc'].mean(), '4f')
    start_coords = (lat, long)
    folium_map = folium.Map(location=start_coords, zoom_start=6)
    html = """
        <h1> Data for this location on {date}</h1><br>
        <p>
        <code>
            Avg TCC: {avg} <br>
            Max TCC: {max} <br>
            Min TCC: {min} <br>
        </code>
        </p>
        """.format(date=date, avg=tcc_avg, max=tcc_max, min=tcc_min)
    iframe = folium.IFrame(html=html, width=200, height=300)
    popup = folium.Popup(iframe, max_width=2650)

    folium.Marker([lat, long], popup=popup).add_to(folium_map)
    return folium_map._repr_html_()


@lambda_handler.route('/from_file/get_daily_json', methods=['GET'])
def get_data_data_json_file():
    date = request.args.get('date')
    lat = request.args.get('lat')
    long = request.args.get('long')
    data_df = select_object(date)
    filtered_df, time_df = filter_df_lat_long(data_df, lat, long)
    tcc_max = format(filtered_df['tcc'].max(), '4f')
    tcc_min = format(filtered_df['tcc'].min(), '4f')
    tcc_avg = format(filtered_df['tcc'].mean(), '4f')

    return_data = {
        'Latitude': lat,
        'Longitude': long,
        'TCC_max': tcc_max,
        'TCC_min': tcc_min,
        'TCC_mean': tcc_avg,
        'Date': date
    }
    return return_data


@lambda_handler.route('/from_file/get_daily_heat_map', methods=['GET'])
def get_data_heat_map_for_day_file():
    date = request.args.get('date')
    lat = request.args.get('lat')
    long = request.args.get('long')
    data_df = select_object(date)
    data_df = data_df[(data_df['long'] >= float(lat)) & (data_df['long'] <= float(lat) + 2)]
    data_df = data_df[(data_df['lat'] >= float(long)) & (data_df['lat'] <= float(long)+ 2)]
    data_df = data_df[['lat', 'long', 'tcc']]
    # heat_data = [[[row['lat'], row['long']] for index, row in data_df[data_df['tcc'] == i].iterrows()] for
    #              i in range(0, 600)]

    start_coords = [lat, long]
    lats = list(data_df['lat'])
    longs =list(data_df['long'])
    folium_map = folium.Map(location=start_coords, zoom_start=14.5)
    heatmap = HeatMap(list(zip(lats, longs, data_df["tcc"])),
                      min_opacity=0.2,
                      max_val=1,
                      radius=50, blur=50,
                      max_zoom=1)
    # add heatmap layer to base map
    heatmap.add_to(folium_map)

    # Display the map
    return folium_map._repr_html_()


@lambda_handler.route('/ping/answer', methods=['GET'])
def get_answer():
    '''
    Example of getting someething from function.properties

    Args:
        None

    Returns:
        tuple of (body, status code, content type) that API Gateway understands
    '''
    return (
        os.environ.get('ANSWER', '99'),
        200,
        {'Content-Type': 'text/html'}
    )


@lambda_handler.route('/ping', methods=['GET'])
def get_ping():
    '''
    Example of getting someething from function.properties

    Args:
        None

    Returns:
        tuple of (body, status code, content type) that API Gateway understands
    '''
    return 'pong'


if __name__ == '__main__':
    lambda_handler.run(debug=True)
