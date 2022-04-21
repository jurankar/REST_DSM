import requests
from django.shortcuts import render
from django.http import JsonResponse
import json

from rest_framework.decorators import api_view
from rest_framework.response import Response

# Create your views here.
@api_view(['GET'])
def restResponse(request):

    # check for zero or multiple query parameters
    airTempPresent = True if 'queryAirportTemp' in request.GET else False
    stoPricePresent = True if 'queryStockPrice' in request.GET else False
    evalPresent = True if 'queryEval' in request.GET else False

    mode = 0 # 1=airport temperature, 2=stocks, 3=evaluating, -1 more or less than 1 parameter
    if airTempPresent and not stoPricePresent and not evalPresent:
        mode = 1
    elif not airTempPresent and stoPricePresent and not evalPresent:
        mode = 2
    elif not airTempPresent and not stoPricePresent and evalPresent:
        mode = 3
    else:
        mode = -1


    if mode == 0:
        result = "error"

    elif mode == -1:
        result = None

    elif mode == 1:
        # airport
        baseApiUrlAirport = "https://www.airport-data.com/api/ap_info.json?iata="
        iataCode = request.GET.get("queryAirportTemp")
        url = baseApiUrlAirport + iataCode
        res = json.loads(requests.get(url).text)

        lat = res["latitude"]
        long = res["longitude"]

        # location
        urlLocation = " http://dataservice.accuweather.com/locations/v1/cities/geoposition/search?apikey=A79lROjjMQ2FIzBLbUBJcqD6pJIRYy6B&q=" + lat + "%2C" + long
        resLocation = json.loads(requests.get(urlLocation).text)
        locationKey = resLocation["Key"]

        # temperature
        urlTemp = "http://dataservice.accuweather.com/currentconditions/v1/" + locationKey + "?apikey=A79lROjjMQ2FIzBLbUBJcqD6pJIRYy6B"
        resTemp = json.loads(requests.get(urlTemp).text)
        result = str(resTemp[0]["Temperature"]["Metric"]["Value"])

    elif mode == 2:
        # stocks
        stockSymbol = request.GET.get("queryStockPrice")
        url = "https://yh-finance.p.rapidapi.com/stock/v2/get-summary"
        querystring = {"symbol": stockSymbol}
        headers = {
            "X-RapidAPI-Host": "yh-finance.p.rapidapi.com",
            "X-RapidAPI-Key": "db961d6974msh31a5b7ba8a92303p14863fjsn5c070139a9bd"
        }

        res = json.loads(requests.request("GET", url, headers=headers, params=querystring).text)
        result = res["price"]["regularMarketPrice"]["raw"]

    elif mode == 3:
        # parsing expressions
        expression = request.build_absolute_uri().split("=")[1]
        result = eval(expression)


    # final response
    jsonRes = JsonResponse({
        "result": result
    })
    return jsonRes