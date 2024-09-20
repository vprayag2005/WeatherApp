from django.urls import path
from . import views

urlpatterns = [
    path('newsglobal/', views.news_global),
    path('news/', views.news,name='global_news'),
    path('newsnational/', views.news_national,name='national_news'),
    path('newssports/', views.tests,name='Sports'),
    #path('newssports/', ),
    
]
