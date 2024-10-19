from django.urls import path
from . import views

urlpatterns = [
    path('globalweathernews/', views.globalnews,name='global_news'),
    path('newsglobal/', views.news_global),
    path('newsnational/', views.news_national),
    path('nationalweathernews/', views.nationalnews,name='national_news'),
    path('newskerala/', views.news_kerala),
    path('keralaweathernews/', views.keralanews,name='kerala_news'),
    
]
