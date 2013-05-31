from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    ( r'^init/$', M6TollAppV2.views.init),
    ( r'^map/$', M6TollAppV2.views.showMap),
    ( r'^route/(?P<fromX>.+)/(?P<fromY>.+)/(?P<toX>.+)/(?P<toY>.+)/$', M6TollAppV2.views.getRoute),
    ( r'^route2/(\d+)/(\d+)/(\d+)/(\d+)/$', M6TollAppV2.views.getRoute),
)



