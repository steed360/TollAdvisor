from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render_to_response

import settings
import RoutingFacade


def loadData ():
    print "l1"


def init (request):

    loadData ()
    print "init done"
    return HttpResponse ("init done")

def showMap (request):

    print settings.STATIC_ROOT
    print "---------------------------"
    print "STATIC_URL is " + settings.STATIC_URL
    print "---------------------------"
    return render_to_response ( "M6.html",{"server":request.META['HTTP_HOST']})


def getRoute (request, fromX, fromY, toX, toY ):

    print "in get route : %s, %s " %(fromX, toX)

    JSON_Result  =  RoutingFacade.findRoute (fromX, fromY, toX, toY )
    return HttpResponse (JSON_Result)

import Geocoder 
import json

def geocode (request, txtLocation ):
    resultDict =  Geocoder.geocode ( txtLocation )
    # resultDict = { txtLocation: a, longitude: b, latitude }

    if resultDict["display_name"]== None:
         resultDict["display_name"] = "Location Not Found"
    JSON_Result = json.dumps ( resultDict )
    return HttpResponse (JSON_Result)



