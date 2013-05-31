from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render_to_response


def loadData ():
    print "l1"


def init (request):

    loadData ()
    print "init done"
    return HttpResponse ("init done")

def showMap (request):

    import settings
    print settings.STATIC_ROOT
    print "STATIC_URL is " + settings.STATIC_URL

    return render_to_response ( "M6.html",{"server":request.META['HTTP_HOST']})


def getRoute (request, fromX, fromY, toX, toY ):





