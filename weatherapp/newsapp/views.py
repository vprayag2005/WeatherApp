from django.shortcuts import render
from django.http import JsonResponse

def tests(request):
    print(request)
    return render(request,'sports.html')
def news_national(request):
    print(request)
    return render(request,'national_news.html')

def news(request):
    return render(request,'global_news.html')
def news_global(request):
    data = {
        'key1': 'value1',
        'key2': 'value2',
    }
    return JsonResponse(data)
def news_sports(request):
    print(request)
    return render(request,'sports.html')
