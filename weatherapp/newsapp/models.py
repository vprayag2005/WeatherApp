from django.db import models

class GlobalNews(models.Model):
    headline=models.CharField(max_length=255)
    news_link=models.URLField(max_length=2083)
    img_link=models.URLField(max_length=2083)
    
    def __str__(self) :
        return self.headline
