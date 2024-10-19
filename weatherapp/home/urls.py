from django.urls import path
from . import views

urlpatterns = [
    path('', views.index,name='home'),
    path('radar/', views.radar,name='radar'),
    path('fetch-data/', views.fetch_data, name='fetch_data'),
    path('settings/',views.settings,name="settings")
]
