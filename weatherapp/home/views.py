import requests
import os

from django.conf import settings as django_settings
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from home.models import UserSettings
from home.utils import (
    COUNTRY_SUGGESTIONS,
    INDIAN_STATE_SUGGESTIONS,
    country_name_from_code,
    join_place_parts,
    normalize_place_name,
    normalize_whitespace,
)


def index(request):
    saved_home_label = request.user_settings.home_location_label

    return render(
        request,
        "index.html",
        {
            "weather_mode": "home",
            "hero_kicker": "Home weather",
            "hero_title": "Welcome back.",
            "hero_description": (
                "Your homepage tries live browser weather first and can fall back "
                "to your saved home location when location access is unavailable."
            ),
            "saved_home_label": saved_home_label,
            "saved_home_query": request.user_settings.city,
        },
    )


def find_weather(request):
    return render(
        request,
        "index.html",
        {
            "weather_mode": "search",
            "hero_kicker": "Find weather",
            "hero_title": "Search weather for any other place.",
            "hero_description": (
                "Keep your homepage focused on your live location and use this page "
                "to check conditions anywhere else."
            ),
        },
    )


def radar(request):
    return render(request, "radar.html")


def settings(request):
    profile = getattr(request, "user_settings", None)
    is_first_run = profile is None
    form_values = {
        "city": profile.city if profile else "",
        "country": profile.country if profile else "India",
        "state": profile.state if profile else "",
    }
    form_errors = {}

    if request.method == "POST":
        form_values = {
            "city": request.POST.get("city", ""),
            "country": request.POST.get("country", ""),
            "state": request.POST.get("state", ""),
        }
        cleaned_values, form_errors = _validate_settings_form(form_values)

        if not form_errors:
            UserSettings.objects.update_or_create(
                visitor_id=request.visitor_id,
                defaults=cleaned_values,
            )
            if is_first_run:
                return redirect("home")
            return redirect(f"{reverse('settings')}?saved=1")

    return render(
        request,
        "settings.html",
        {
            "country_suggestions": COUNTRY_SUGGESTIONS,
            "form_errors": form_errors,
            "form_values": form_values,
            "is_first_run": is_first_run,
            "saved": request.GET.get("saved") == "1",
            "should_auto_locate": is_first_run
            and not normalize_whitespace(form_values.get("city", ""))
            and not normalize_whitespace(form_values.get("state", "")),
            "state_suggestions": INDIAN_STATE_SUGGESTIONS,
        },
    )


def resolve_location(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request"}, status=400)

    latitude = request.POST.get("lat")
    longitude = request.POST.get("lon")

    try:
        latitude = float(latitude)
        longitude = float(longitude)
    except (TypeError, ValueError):
        return JsonResponse({"error": "A valid location is required."}, status=400)

    try:
        geo_resp = requests.get(
            "https://api.openweathermap.org/geo/1.0/reverse",
            params={
                "lat": latitude,
                "lon": longitude,
                "limit": 1,
                "appid": os.getenv('OPENWEATHER_API_KEY'),
            },
            timeout=15,
        )
        geo_data = geo_resp.json()

        if isinstance(geo_data, dict):
            return JsonResponse(
                {
                    "error": f'API Error: {geo_data.get("message", "Reverse geocoding failed")}'
                },
                status=geo_resp.status_code,
            )

        if not geo_data:
            return JsonResponse(
                {"error": "We could not determine your city from that location."},
                status=404,
            )

        place = geo_data[0]
        city = normalize_place_name(place.get("name", ""))
        state = normalize_place_name(place.get("state", ""))
        country = country_name_from_code(place.get("country", ""))

        return JsonResponse(
            {
                "city": city,
                "state": state,
                "country": country,
                "label": join_place_parts(city, state, country),
            }
        )
    except Exception as exc:
        return JsonResponse({"error": str(exc)}, status=500)


@csrf_exempt
def fetch_data(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request'}, status=400)

    city = normalize_whitespace(request.POST.get("city", ""))
    latitude = request.POST.get("lat")
    longitude = request.POST.get("lon")

    import os; apikey = os.getenv('OPENWEATHER_API_KEY')

    try:
        if city:
            geo_resp = requests.get(
                "https://api.openweathermap.org/geo/1.0/direct",
                params={"q": city, "limit": 1, "appid": apikey},
                timeout=15,
            )
            geo_data = geo_resp.json()

            if isinstance(geo_data, dict):
                return JsonResponse(
                    {"error": f'API Error: {geo_data.get("message", "Geocoding failed")}'},
                    status=geo_resp.status_code,
                )
            if not geo_data:
                return JsonResponse({"error": f'City "{city}" not found'}, status=404)

            latitude = geo_data[0]["lat"]
            longitude = geo_data[0]["lon"]
        elif latitude and longitude:
            latitude = float(latitude)
            longitude = float(longitude)
        else:
            return JsonResponse(
                {"error": "A city or current location is required."},
                status=400,
            )

        weather_resp = requests.get(
            "https://api.openweathermap.org/data/2.5/weather",
            params={
                "lat": latitude,
                "lon": longitude,
                "units": "metric",
                "appid": apikey,
            },
            timeout=15,
        )
        weather_data = weather_resp.json()
        if str(weather_data.get("cod")) != "200":
            return JsonResponse(
                {"error": f'API Error: {weather_data.get("message", "Weather fetch failed")}'},
                status=weather_resp.status_code,
            )

        forecast_resp = requests.get(
            "https://api.openweathermap.org/data/2.5/forecast",
            params={
                "lat": latitude,
                "lon": longitude,
                "units": "metric",
                "appid": apikey,
            },
            timeout=15,
        )
        forecast_data = forecast_resp.json()
        if str(forecast_data.get("cod")) != "200":
            return JsonResponse(
                {"error": f'API Error: {forecast_data.get("message", "Forecast fetch failed")}'},
                status=forecast_resp.status_code,
            )

        return JsonResponse([weather_data, forecast_data], safe=False)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def _validate_settings_form(form_values):
    cleaned_values = {
        "city": normalize_place_name(form_values.get("city", "")),
        "country": normalize_place_name(form_values.get("country", "")),
        "state": normalize_place_name(form_values.get("state", "")),
    }
    errors = {}

    if not cleaned_values["city"]:
        errors["city"] = "Please enter your city."
    else:
        import requests, os
        apikey = os.getenv('OPENWEATHER_API_KEY')
        if apikey:
            try:
                geo_resp = requests.get(
                    "https://api.openweathermap.org/geo/1.0/direct",
                    params={"q": cleaned_values["city"], "limit": 1, "appid": apikey},
                    timeout=5,
                )
                geo_data = geo_resp.json()
                if not geo_data or (isinstance(geo_data, dict) and "message" in geo_data):
                    errors["city"] = f"City '{cleaned_values['city']}' was not found in OpenWeatherMap."
            except Exception:
                pass  # Ignore network errors to avoid locking out the user

    if not cleaned_values["country"]:
        errors["country"] = "Please enter your country."

    if not cleaned_values["state"]:
        errors["state"] = "Please enter your state."

    return cleaned_values, errors


from django.http import HttpResponse
def radar_tile(request, layer, z, x, y):
    import os, requests
    api_key = os.getenv('OPENWEATHER_API_KEY')
    url = f'https://tile.openweathermap.org/map/{layer}/{z}/{x}/{y}.png?appid={api_key}'
    try:
        r = requests.get(url, timeout=15)
        return HttpResponse(r.content, content_type='image/png')
    except Exception as e:
        return HttpResponse(status=500)
