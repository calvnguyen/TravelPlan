from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^$', views.index),
    url(r'^login$', views.login),
    url(r'^listing$', views.list_plans),
    url(r'^register$', views.create_user),
    url(r'^logout$', views.logout),
    url(r'^travels/add$', views.create_trip),
    url(r'^travels/destination/(?P<trip_id>\d+)$', views.show),
    url(r'^travels/add_to_plan/(?P<trip_id>\d+)$', views.add_to_plan)
]

