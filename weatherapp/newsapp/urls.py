from django.urls import path
from . import views

urlpatterns = [
    path('globalweathernews/', views.globalnews,name='global_news'),
    path('newsglobal/', views.news_global),
    path('newsnational/', views.news_national),
    path('nationalweathernews/', views.nationalnews,name='national_news'),
    path('stateweathernews/', views.my_state_news, name='my_state_news'),
    path('stateweathernews/<str:state_name>/', views.state_news, name='state_news'),
    path('newsstate/<str:state_name>/', views.news_state),
]
