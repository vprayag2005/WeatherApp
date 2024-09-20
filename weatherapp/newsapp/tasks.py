from newsapp.scrapper import scrap_global
from celery import shared_task

@shared_task
def run_scraper_task():
    # Call the scraper function from scraper.py
    scrap_global()

