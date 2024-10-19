from django.shortcuts import render
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
def radar(request):
    return render(request,'radar.html')
def index(request):
    return render(request,'index.html')
@csrf_exempt
def fetch_data(request):
    if request.method == 'POST':
        city = request.POST.get('city')
        apikey = "08e1d68746a3ed8abfd71233a74b98c7"
        curent_weather_url="https://api.openweathermap.org/data/2.5/weather?&units=metric&q="
        hourlyurl = "https://api.openweathermap.org/data/2.5/forecast?&units=metric&q="
        print(city)
        if city:
            try:
                # Fetch data from an API (replace with your API URL)
                api_url_curent=f'{curent_weather_url}{city}&appid={apikey}'
                api_response_1 = requests.get(api_url_curent)
                api_data_1 = api_response_1.json()
                api_url_hourly=f'{hourlyurl}{city}&appid={apikey}'
                api_response_2 = requests.get(api_url_hourly)
                api_data_2 = api_response_2.json()
                # Convert to JSON and send response
                return JsonResponse([api_data_1,api_data_2], safe=False)
            except Exception as e:
                return JsonResponse({'error': str(e)}, status=500)
        else:
            return JsonResponse({'error': 'City not provided'}, status=400)
    return JsonResponse({'error': 'Invalid request'}, status=400)

def settings(request):
    return render(request,"settings.html")
    
