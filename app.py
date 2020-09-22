from  flask import Flask, escape, request
from  flask_cors import CORS, cross_origin
import time
from datetime import date, datetime
import json
import requests
from password import getUSGSPassword, getNOAAToken
import pandas as pd
import io
import landsatxplore.api
from dateutil.relativedelta import *


app = Flask(__name__)
CORS(app)


def callNOAAapi(url, params, header):
    r = requests.get(url, params, headers=header).text
    rawData = pd.read_csv(io.StringIO(r))
    return rawData

@app.route('/api/getNOAAdata', methods=['POST'])
def getNOAAdata():
    data = json.loads(request.data)

    startDate = data['startDate']
    endDate = data['endDate']

    token = getNOAAToken()
    
    creds = dict(token=token)
    params = {'dataset': 'daily-summaries', \
            'stations': 'USR0000CALP',\
            'startDate': startDate, 'endDate': endDate,  \
            'dataTypes': ['AWND', 'PRCP', 'SNOW', 'TAVG', 'WT01', 'TMAX', 'TMIN'], \
            'units': 'standard'}
    url = 'https://www.ncei.noaa.gov/access/services/data/v1'

    urlData = callNOAAapi(url, params, creds)
    dataHead = urlData.head(10)
    result = {
        'rawData': dataHead.to_json(),
        'totalDataLength': len(urlData),
        # 'startDate': monthAgo,
        # 'endDate': today
    }
    return result


@app.route('/api/getEarthExplorerData', methods=['POST'])
def getEarthExplorerData():
    data = json.loads(request.data)
    lat = float(data['lat'])
    lon = float(data['lon'])
    startDate = data['startDate']
    endDate = data['endDate']

    # today = date.today()
    # yearAgo = today + relativedelta(years = -1)
    # today = today.strftime('%Y-%m-%d')
    # yearAgo = yearAgo.strftime('%Y-%m-%d')

    password = getUSGSPassword()
    api = landsatxplore.api.API('sukhvir', password)
    scenes = api.search(
        dataset = 'LANDSAT_ETM_C1',
        latitude = lat,
        longitude = lon,
        start_date = startDate,
        end_date = endDate,
        max_cloud_cover = 10
    )
    api.logout()

    result = {
        'scenes': scenes[0:10],
        'totalDataLength': len(scenes),
        # 'startDate': yearAgo,
        # 'endDate': today,
    }
    return result

@app.route('/api/getUSDAFireData', methods=['POST'])
def getUSDAFireData():
    data = json.loads(request.data)
    start_year = data['startYear']
    end_year = data['endYear']

    if start_year == end_year:
        sqlQuery =  f"STATE_NAME = 'CA - CALIFORNIA' and DISCOVER_YEAR = {start_year}" 
    elif start_year > end_year:
        sqlQuery = "STATE_NAME = 'CA - CALIFORNIA' and DISCOVER_YEAR = 0" 
    elif start_year < end_year:
        sqlQuery = f"STATE_NAME = 'CA - CALIFORNIA' and DISCOVER_YEAR between {start_year} and {end_year}"
    
    url = "https://apps.fs.usda.gov/arcx/rest/services/EDW/EDW_FireOccurrenceFIRESTAT_YRLY_01/MapServer/0/query"
    outFields = "OBJECTID, DISCOVER_YEAR, STATE_NAME, COUNTY_NAME, FIRE_SIZE_CLASS, POO_LATITUDE, POO_LONGITUDE"
    params = {"outSR": "4326",
              "where": sqlQuery,
              "outFields": outFields,
              "f":"json"}

    r = requests.get(url, params)
    data = r.text
    data = json.loads(data)

    # for i in range(len(data['features'])):
    #     print(data['features'][i]['attributes'])

    result = {
        'data': data
    }
    return result

@app.route('/api/getFirestatData')
def getFirestatData():
    pass

@app.route('/api/getNasaLandsatData', methods=['POST'])
def getNasaLandsatData():
    pass

@app.route('/api/getGoogleEarthEngineData', methods=['POST'])
def getGoogleEarthEngineData():
    pass

@app.route('/api/getModisData', methods=['POST'])
def getModisData():
    pass




# the code below is just for the flask examples

database = {
    1: 'one',
    2: 'two',
    3: 'three',
    4: 'four'
}

optionSelected = None

@app.route('/')
def index():
    return 'This is the flask backend for the wildfire project'

@app.route('/api/time')
def get_current_time():
    return {'time': time.time()}

@app.route('/api/handle-select', methods=['POST'])
def handle_select():
    global optionSelected
    data = json.loads(request.data)
    optionSelected = data['optionSelected']
    return {'optionSelected': optionSelected}

@app.route('/api/get-select')
def get_select():
    global optionSelected
    return {'optionSelected': optionSelected}

@app.route('/api/sum')
def sum():
    num1 = request.args['num1']
    num2 = request.args['num2']

    if(num1 == '' or num2 == ''):
        return {'sum': 'Please enter a value for both numbers'}

    result = calculateSum(float(num1), float(num2))
    return {'sum': result}

def calculateSum(num1, num2):
    return num1 + num2


@app.route('/api/database/<index>')
def indexDatabase(index):
    global database
    index = int(index)
    if index >= len(database) or index < 1:
        return {'result':"No entry at index "+ str(index)}
    return {'result': database[index]}



if __name__ == '__main__':
    app.run(host="0.0.0.0", threaded=True, port=5000)