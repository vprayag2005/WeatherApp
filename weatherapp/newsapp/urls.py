from django.urls import path
from . import views

urlpatterns = [
    path('globalweathernews/', views.globalnews,name='global_news'),
    path('newsglobal/', views.news_global),
    path('newsnational/', views.news_national,name='national_news'),
    path('newssports/', views.tests,name='Sports'),
    #path('newssports/', ),
    
]
