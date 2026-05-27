from django.http import JsonResponse
from django.shortcuts import redirect, render

from home.utils import display_state_name, normalize_state_key, state_slug
from newsapp.models import GlobalNews, NationalNews, StateNews
from newsapp.scrapper import scrape_news


# ---------------------------------------------------------------------------
# Page views
# ---------------------------------------------------------------------------

def globalnews(request):
    return render(request, 'global_news.html')


def nationalnews(request):
    return render(request, 'national_news.html')


def my_state_news(request):
    return redirect("state_news", state_name=state_slug(request.user_settings.state))


def state_news(request, state_name):
    normalized_state = normalize_state_key(state_name)
    return render(
        request,
        "state_news.html",
        {
            "state_label": display_state_name(normalized_state),
            "state_name": state_slug(normalized_state),
        },
    )


# ---------------------------------------------------------------------------
# JSON API views  (used by frontend to fetch news data)
# ---------------------------------------------------------------------------

def news_global(request):
    data = {
        'headlines':  list(GlobalNews.objects.values('headline')),
        'news_links': list(GlobalNews.objects.values('news_link')),
        'pubDates':   list(GlobalNews.objects.values('pubDate')),
        'sources':    list(GlobalNews.objects.values('source')),
    }
    return JsonResponse(data)


def news_national(request):
    data = {
        'headlines':  list(NationalNews.objects.values('headline')),
        'news_links': list(NationalNews.objects.values('news_link')),
        'pubDates':   list(NationalNews.objects.values('pubDate')),
        'sources':    list(NationalNews.objects.values('source')),
    }
    return JsonResponse(data)


def news_state(request, state_name):
    normalized_state = normalize_state_key(state_name)
    news_qs = StateNews.objects.filter(state_name__iexact=normalized_state)

    if not news_qs.exists():
        scrape_news(normalized_state)
        news_qs = StateNews.objects.filter(state_name__iexact=normalized_state)

    data = {
        'headlines':  list(news_qs.values('headline')),
        'news_links': list(news_qs.values('news_link')),
        'pubDates':   list(news_qs.values('pubDate')),
        'sources':    list(news_qs.values('source')),
    }
    return JsonResponse(data)
