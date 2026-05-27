from newsapp.scrapper import scrap_global, scrap_national, scrape_news
from celery import shared_task

@shared_task
def run_scraper_task():
    # Call the scraper function from scraper.py
    scrap_global()
    scrap_national()
    
    # List of Indian states to fetch news for. Add more as needed.
    states_to_scrape = ["kerala", "karnataka", "maharashtra", "delhi", "tamil nadu", "gujarat"]
    for state in states_to_scrape:
        scrape_news(state)
        
    print("Scraping task completed")

