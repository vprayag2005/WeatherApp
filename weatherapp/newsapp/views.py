from django.shortcuts import render
from django.http import JsonResponse
from newsapp.models import GlobalNews,NationalNews,KeralaNews,KarnatakaNews

def nationalnews(request):
    return render(request,'national_news.html')
def news_national(request):
    headlines=list(NationalNews.objects.values('headline'))
    images_link=list(NationalNews.objects.values('img_link'))
    news_link=list(NationalNews.objects.values('news_link'))
    data = {
        'headlines':headlines,
        'images_link': images_link,
        'news_link': news_link,
    }
    return JsonResponse(data)

def globalnews(request):
    return render(request,'global_news.html')
def news_global(request):
    headlines=list(GlobalNews.objects.values('headline'))
    images_link=list(GlobalNews.objects.values('img_link'))
    news_link=list(GlobalNews.objects.values('news_link'))
    data = {
        'headlines':headlines,
        'images_link': images_link,
        'news_link': news_link,
    }
    return JsonResponse(data)
def keralanews(request):
    return render(request,'kerala_news.html')
def news_kerala(request):
    headlines=list(KeralaNews.objects.values('headline'))
    images_link=list(KeralaNews.objects.values('img_link'))
    news_link=list(KeralaNews.objects.values('news_link'))
    data = {
        'headlines':headlines,
        'images_link': images_link,
        'news_link': news_link,
    }
    return JsonResponse(data)
def karnatakanews(requests):
    return render(requests,"karnataka_news.html")
def news_karnataka(request):
    headlines=list(KarnatakaNews.objects.values('headline'))
    news_link=list(KarnatakaNews.objects.values('news_link'))
    pubdates=list(KarnatakaNews.objects.values('pubDate'))
    sources=list(KarnatakaNews.objects.values('source'))
    data = {
        'headlines':headlines,
        'news_links': news_link,
        'pubDates': pubdates,
        'Sources': sources,
        
    }
    return JsonResponse(data)