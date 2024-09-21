from django.shortcuts import render
from django.http import JsonResponse
from newsapp.models import GlobalNews

def tests(request):
    print(request)
    return render(request,'sports.html')
def news_national(request):
    print(request)
    return render(request,'national_news.html')

def globalnews(request):
    return render(request,'global_news.html')
def news_global(request):
    print(GlobalNews.objects.values('img_link'))
    headlines=list(GlobalNews.objects.values('headline'))
    images_link=list(GlobalNews.objects.values('img_link'))
    news_link=list(GlobalNews.objects.values('news_link'))
    print(images_link)
    data = {
        'headlines':headlines,
        'images_link': images_link,
        'news_link': news_link,
    }
    return JsonResponse(data)
def news_sports(request):
    print(request)
    return render(request,'sports.html')
