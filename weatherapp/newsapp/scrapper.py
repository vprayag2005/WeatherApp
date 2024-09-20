import requests
from bs4 import BeautifulSoup
from newsapp.models import GlobalNews
def scrap_global():
    # URL to scrape
    url = "https://edition.cnn.com/weather"

    # Make a request to the website
    try:
        req = requests.get(url)
        req.raise_for_status()  # Check for HTTP errors
        soup = BeautifulSoup(req.content, 'lxml')
    except requests.RequestException as e:
        raise

    # Find different types of news items
    parrent_video = soup.find_all('a', class_='container__link container__link--type-video container_lead-plus-headlines-with-images__link')
    parrent_article = soup.find_all('a', class_='container__link container__link--type-article container_lead-plus-headlines-with-images__link')
    parrent_livestory = soup.find_all('a', class_='container__link container__link--type-live-story container_lead-plus-headlines-with-images__link')
    parrent_bottom_article = soup.find_all('a', class_='container__link container__link--type-article container_grid-4__link')
    parrent_bottom_video = soup.find_all('a', class_='container__link container__link--type-video container_grid-4__link')
    parrent_side = soup.find_all('a', class_='container__link container__link--type-article container_vertical-strip__link container_vertical-strip__left container_vertical-strip__light')

    # Initialize lists to hold scraped data
    headlines = []
    links = []
    img_src = []

    def scrape_globalnews(parrent):
        for item in parrent:
            try:
                # Extract headlines
                headline = item.find('span', class_='container__headline-text')
                if headline:
                    headlines.append(headline.get_text())
                
                # Extract links and image sources
                href = item.get('href')
                if href:
                    full_link = "https://edition.cnn.com" + href
                    links.append(full_link)
                    
                    picture = item.find('picture', class_='image__picture')
                    if picture:
                        img = picture.find('source')
                        if img:
                            img_src.append(img.get('srcset'))
            except Exception as e:
                pass

    def dataglobal():
        # Clear existing entries
        GlobalNews.objects.all().delete()
        
        # Insert new data
        for headline, link, img in zip(headlines, links, img_src):
            try:
                GlobalNews.objects.create(headline=headline, news_link=link, img_link=img)
            except Exception as e:
                pass

    # Scrape data
    scrape_globalnews(parrent_video)
    scrape_globalnews(parrent_article)
    scrape_globalnews(parrent_livestory)
    scrape_globalnews(parrent_side)
    scrape_globalnews(parrent_bottom_video)
    scrape_globalnews(parrent_bottom_article)

    # Save data to the database
    dataglobal()
