from django.http import JsonResponse
from django.shortcuts import render

from alertsapp.models import SubdivisionAlert
from alertsapp.services import build_feature_collection, sync_subdivision_alerts, DISTRICT_WISE_URLS
from alertsapp.models import DistrictAlertImage


def statewise_alerts(request):
    return render(
        request,
        "statewise_alerts.html",
        {
            "default_day": 1,
            "preferred_subdivision": request.GET.get("subdivision", ""),
            "preferred_state": getattr(getattr(request, "user_settings", None), "state", ""),
        },
    )


def districtwise_alerts(request):
    images = DistrictAlertImage.objects.all()
    # Format: {"State Name": {"1": "url1", "2": "url2", ...}}
    image_dict = {}
    for img in images:
        if img.image:
            if img.state_name not in image_dict:
                image_dict[img.state_name] = {}
            image_dict[img.state_name][str(img.day_number)] = img.image.url

    import json
    import datetime
    
    # Generate dates for Day 1 to Day 5 in IST
    ist_tz = datetime.timezone(datetime.timedelta(hours=5, minutes=30))
    today = datetime.datetime.now(tz=ist_tz).date()
    days_list = []
    for i in range(1, 6):
        target_date = today + datetime.timedelta(days=i - 1)
        days_list.append({
            "value": i,
            "label": f"Day {i} - {target_date.strftime('%b %d, %Y')}"
        })

    return render(
        request,
        "districtwise_alerts.html",
        {
            "states_list": list(DISTRICT_WISE_URLS.keys()),
            "preferred_state": getattr(getattr(request, "user_settings", None), "state", ""),
            "images_dict": json.dumps(image_dict),
            "days_list": days_list,
        },
    )


def statewise_alerts_data(request):
    alerts = SubdivisionAlert.objects.all()
    if not alerts.exists():
        try:
            sync_subdivision_alerts()
        except Exception as exc:
            return JsonResponse(
                {"error": f"Unable to sync live alerts right now: {exc}"},
                status=502,
            )
        alerts = SubdivisionAlert.objects.all()

    return JsonResponse(build_feature_collection(alerts))
