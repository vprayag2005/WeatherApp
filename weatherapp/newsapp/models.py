from django.db import models


class GlobalNews(models.Model):
    headline  = models.CharField(max_length=500)
    news_link = models.URLField(max_length=2083)
    pubDate   = models.CharField(max_length=255, blank=True, default="")
    source    = models.CharField(max_length=255, blank=True, default="")

    def __str__(self):
        return f"{self.headline} | {self.source}"


class NationalNews(models.Model):
    headline  = models.CharField(max_length=500)
    news_link = models.URLField(max_length=2083)
    pubDate   = models.CharField(max_length=255, blank=True, default="")
    source    = models.CharField(max_length=255, blank=True, default="")

    def __str__(self):
        return f"{self.headline} | {self.source}"


class StateNews(models.Model):
    state_name = models.CharField(max_length=100)
    headline  = models.CharField(max_length=500)
    news_link = models.URLField(max_length=2083)
    pubDate   = models.CharField(max_length=255, blank=True, default="")
    source    = models.CharField(max_length=255, blank=True, default="")

    def __str__(self):
        return f"[{self.state_name}] {self.headline} | {self.source}"