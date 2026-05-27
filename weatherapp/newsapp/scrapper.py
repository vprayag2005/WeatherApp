import requests
from bs4 import BeautifulSoup
from newsapp.models import GlobalNews, NationalNews, StateNews
from datetime import date
from email.utils import parsedate_to_datetime


# ---------------------------------------------------------------------------
# Unified Google News RSS scraper
# ---------------------------------------------------------------------------

def _is_today(pub_date_str: str) -> bool:
    """Return True if the pubDate string corresponds to today's date."""
    if not pub_date_str:
        return False
    try:
        article_date = parsedate_to_datetime(pub_date_str).date()
        return article_date == date.today()
    except Exception:
        return False


def _fetch_google_news_rss(query: str, hl: str = "en-IN", gl: str = "IN", ceid: str = "IN:en") -> list[dict]:
    """
    Fetch today's English news items from Google News RSS for the given search query.

    Returns a list of dicts with keys: headline, news_link, pubDate, source
    """
    today_str = date.today().strftime("%Y-%m-%d")
    # Append after: filter to get only today's news; use English locale
    full_query = f"{query} after:{today_str}"
    url = (
        f"https://news.google.com/rss/search"
        f"?q={requests.utils.quote(full_query)}"
        f"&hl={hl}&gl={gl}&ceid={ceid}"
    )
    results = []
    try:
        req = requests.get(url, timeout=15)
        req.raise_for_status()
        soup = BeautifulSoup(req.content, "xml")
        for item in soup.find_all("item"):
            title_tag  = item.find("title")
            link_tag   = item.find("link")
            date_tag   = item.find("pubDate")
            source_tag = item.find("source")

            headline  = title_tag.get_text(strip=True)  if title_tag  else ""
            news_link = link_tag.get_text(strip=True)   if link_tag   else ""
            pub_date  = date_tag.get_text(strip=True)   if date_tag   else ""
            source    = source_tag.get_text(strip=True) if source_tag else ""

            # Skip articles that are not from today (double-check)
            if not _is_today(pub_date):
                continue

            if headline and news_link:
                results.append({
                    "headline":  headline,
                    "news_link": news_link,
                    "pubDate":   pub_date,
                    "source":    source,
                })
    except Exception as e:
        print(f"[RSS] Error fetching '{query}': {e}")
    return results


# ---------------------------------------------------------------------------
# Per-category scrapers  (each calls the shared helper)
# ---------------------------------------------------------------------------

def scrap_global():
    """Fetch global weather news via Google News RSS."""
    items = _fetch_google_news_rss(
        query="global weather",
        hl="en-US",
        gl="US",
        ceid="US:en",
    )
    GlobalNews.objects.all().delete()
    for item in items:
        try:
            GlobalNews.objects.create(
                headline=item["headline"],
                news_link=item["news_link"],
                pubDate=item["pubDate"],
                source=item["source"],
            )
        except Exception as e:
            print(f"[GlobalNews] DB error: {e}")


def scrap_national():
    """Fetch India national weather news via Google News RSS."""
    items = _fetch_google_news_rss(
        query="India weather",
        hl="en-IN",
        gl="IN",
        ceid="IN:en",
    )
    NationalNews.objects.all().delete()
    for item in items:
        try:
            NationalNews.objects.create(
                headline=item["headline"],
                news_link=item["news_link"],
                pubDate=item["pubDate"],
                source=item["source"],
            )
        except Exception as e:
            print(f"[NationalNews] DB error: {e}")


def scrape_news(state: str):
    """Fetch state-level weather news via Google News RSS."""
    items = _fetch_google_news_rss(
        query=f"{state} weather",
        hl="en-IN",
        gl="IN",
        ceid="IN:en",
    )
    StateNews.objects.filter(state_name=state).delete()
    for item in items:
        try:
            StateNews.objects.create(
                state_name=state,
                headline=item["headline"],
                news_link=item["news_link"],
                pubDate=item["pubDate"],
                source=item["source"],
            )
        except Exception as e:
            print(f"[StateNews] DB error for {state}: {e}")