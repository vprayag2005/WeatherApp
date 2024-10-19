import requests
from bs4 import BeautifulSoup
from newsapp.models import GlobalNews,NationalNews,KeralaNews,KarnatakaNews
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

                    
                picture = item.find('picture', class_='image__picture')
                if picture:
                        if href:
                            full_link = "https://edition.cnn.com" + href
                            links.append(full_link)
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

def scrap_national():
    headlines=[]
    imgs=[]
    links=[]
    url = "https://www.ndtv.com/topic/india-weather"
    req = requests.get(url)
    weather_keywords = [
        "Temperature", "Humidity", "Wind Speed", "Wind Direction", "Precipitation", 
        "Rain", "Snow", "Hail", "Thunderstorm", "Lightning", "Fog", "Mist", 
        "Visibility", "Pressure", "Barometric Pressure", "Dew Point", "Cloud Cover", 
        "UV Index", "Heat Index", "Chill Factor (Wind Chill)", "Tornado", "Cyclone", 
        "Hurricane", "Typhoon", "Storm Surge", "Flood", "Drought", "Air Quality", 
        "Pollen Count", "Heatwave", "Cold Front", "Warm Front", "High Pressure", 
        "Low Pressure", "Jet Stream", "El Niño", "La Niña", "Monsoon", "Tsunami", 
        "Tropical Storm", "Atmospheric River", "Drizzle", "Sleet", "Gale", "Breeze", 
        "Clear Skies", "Overcast", "Partly Cloudy", "Scattered Showers", "Isolated Thunderstorms","Mausam",
        "Imd","Weather"
    ]

    if req.status_code==200: 
        soup = BeautifulSoup(req.content, "lxml")
        ul=soup.find("ul",class_="src_lst-ul")
        li=ul.find_all("li",class_="src_lst-li")
        for i in li:
            title=i.find("div",class_="src_lst-rhs").find("div",class_="src_itm-ttl").find("a").get("title")
            link=i.find("div",class_="src_lst-rhs").find("div",class_="src_itm-ttl").find("a").get("href")
            img=i.find("div",class_="src_lst-lhs").find("span",class_="img-gratio").find("img").get("src")
            if any(keyword.lower() in title.lower() for keyword in weather_keywords):
                links.append(link)
                headlines.append(title)
                imgs.append(img)
        
    # Clear existing entries
    NationalNews.objects.all().delete()
    
    # Insert new data
    for headline, link, img in zip(headlines, links, imgs):
        try:
            NationalNews.objects.create(headline=headline, news_link=link, img_link=img)
        except Exception as e:
            pass
            
def scrape_kerala():
    url="https://newsable.asianetnews.com/search?topic=kerala-weather-news"
    req=requests.get(url)
    headlines=[]
    news_links=[]
    img_links=[]
    if req.status_code==200:
        soup=BeautifulSoup(req.content,"lxml")
        div=soup.find_all("div",class_="searchright")
        for i in div:
            headline=i.find("a").get_text()
            news_link="https://newsable.asianetnews.com/"+i.find("a").get("href")
            url_img="https://newsable.asianetnews.com/"+i.find("a").get("href")
            req_img=requests.get(url_img)
            if req_img.status_code==200:
                soup_img=BeautifulSoup(req_img.content,"lxml")
                img_link=soup_img.find("div",class_="pure-u-1 mainimg lozad").find("picture").find("img").get("src")
            headlines.append(headline)
            news_links.append(news_link)
            img_links.append(img_link)
    
    KeralaNews.objects.all().delete()
    
    for headline,news_link,img_link in zip(headlines,news_links,img_links):
        print(headline)
        try:
            KeralaNews.objects.create(headline=headline,news_link=news_link,img_link=img_link)
        except Exception as e :
            pass

def scrape_news(state):
    headlines,news_links,pubdates,sources=[],[],[],[]
    url=f'https://news.google.com/rss/search?q={state}+weather&hl=en-IN&gl=IN&ceid=IN:en'
    req=requests.get(url)
    if req.status_code==200:
        soup=BeautifulSoup(req.content,"xml")
        item=soup.find_all("item")
        for i in item:
            headlines.append(i.find("title").get_text())
            news_links.append(i.find("link").get_text())
            pubdates.append(i.find("pubDate").get_text())
            sources.append(i.find("source").get_text())
    
    try:
        KarnatakaNews.objects.all().delete()
        for headline,link,date,source in zip(headlines,news_links,pubdates,sources):
            KarnatakaNews.objects.create(headline=headline,news_link=link,pubDate=date,source=source)
    except Exception as e:
        pass
        
            