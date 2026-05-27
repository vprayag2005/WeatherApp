from django.urls import path
from . import views

urlpatterns = [
    path('', views.index,name='home'),
    path('find-weather/', views.find_weather, name='find_weather'),
    path('radar/', views.radar,name='radar'),
    path('fetch-data/', views.fetch_data, name='fetch_data'),
    path('settings/location/', views.resolve_location, name='resolve_location'),
    path('settings/',views.settings,name="settings"),
    path('radar/tiles/<str:layer>/<int:z>/<int:x>/<int:y>/', views.radar_tile, name='radar_tile'),
]
