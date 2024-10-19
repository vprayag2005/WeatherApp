from newsapp.scrapper import scrap_global,scrap_national,scrape_kerala,scrape_news
from celery import shared_task

@shared_task
def run_scraper_task():
    # Call the scraper function from scraper.py
    #scrap_global()
    #scrap_national()
    #scrape_kerala()
    scrape_news("karnataka")
    print("hai")

