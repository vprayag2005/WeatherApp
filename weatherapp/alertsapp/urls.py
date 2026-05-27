from django.urls import path

from alertsapp import views


urlpatterns = [
    path("statewise/", views.statewise_alerts, name="alerts_statewise"),
    path("districtwise/", views.districtwise_alerts, name="alerts_districtwise"),
    path("api/statewise/", views.statewise_alerts_data, name="statewise_alerts_data"),
]

