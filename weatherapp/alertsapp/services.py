from datetime import timedelta

import requests
from django.db import transaction
from django.utils.dateparse import parse_date, parse_datetime
from django.utils.text import slugify

from alertsapp.models import SubdivisionAlert


IMD_SUBDIVISION_WFS_URL = "https://reactjs.imd.gov.in/geoserver/wfs"
IMD_SUBDIVISION_WFS_PARAMS = {
    "service": "WFS",
    "version": "1.1.0",
    "request": "GetFeature",
    "typename": "imd:subdiv_warnings_now",
    "srsname": "EPSG:4326",
    "outputFormat": "application/json",
}

SEVERITY_META = {
    1: {"label": "No warning", "hex": "#22c55e", "rank": 0},
    2: {"label": "Watch", "hex": "#facc15", "rank": 1},
    3: {"label": "Alert", "hex": "#fb923c", "rank": 2},
    4: {"label": "Warning", "hex": "#ef4444", "rank": 3},
}

WARNING_CODE_LABELS = {
    "1": "No Warning",
    "2": "Heavy Rain",
    "3": "Heavy Snow",
    "4": "Thunderstorm & Lightning",
    "5": "Hailstorm",
    "6": "Dust Storm",
    "7": "Dust Raising Winds",
    "8": "Strong Surface Winds",
    "9": "Heat Wave",
    "91": "Severe Heat Wave",
    "10": "Hot Day",
    "11": "Warm Night",
    "12": "Cold Wave",
    "121": "Severe Cold Wave",
    "13": "Cold Day",
    "131": "Severe Cold Day",
    "14": "Ground Frost",
    "15": "Fog",
    "151": "Dense Fog",
    "152": "Very Dense Fog",
    "16": "Very Heavy Rain",
    "17": "Extremely Heavy Rain",
    "18": "Hot and Humid",
    "41": "Thunderstorm & Lightning",
    "42": "Thunderstorm & Lightning",
    "43": "Thunderstorm & Lightning",
    "44": "Thunderstorm & Lightning",
}


def fetch_subdivision_alert_geojson():
    session = requests.Session()
    session.trust_env = False
    response = session.get(
        IMD_SUBDIVISION_WFS_URL,
        params=IMD_SUBDIVISION_WFS_PARAMS,
        timeout=30,
        headers={"User-Agent": "WeatherApp/1.0"},
    )
    response.raise_for_status()
    payload = response.json()

    if not isinstance(payload, dict) or "features" not in payload:
        raise ValueError("IMD subdivision warning feed returned an unexpected payload.")

    return payload


@transaction.atomic
def sync_subdivision_alerts():
    payload = fetch_subdivision_alert_geojson()
    features = payload.get("features", [])
    seen_slugs = []
    created_count = 0
    updated_count = 0

    for feature in features:
        properties = feature.get("properties") or {}
        subdivision_name = (properties.get("SUBDIV") or "").strip()
        if not subdivision_name:
            continue

        subdivision_slug = slugify(subdivision_name)
        source_date = parse_date(properties.get("Date") or "")
        source_updated_at = parse_datetime(properties.get("updat") or "")

        _, created = SubdivisionAlert.objects.update_or_create(
            subdivision_slug=subdivision_slug,
            defaults={
                "subdivision_name": subdivision_name,
                "source_date": source_date,
                "source_updated_at": source_updated_at,
                "geometry": feature.get("geometry") or {},
                "properties": properties,
            },
        )
        seen_slugs.append(subdivision_slug)
        if created:
            created_count += 1
        else:
            updated_count += 1

    deleted_count = 0
    if seen_slugs:
        deleted_count, _ = SubdivisionAlert.objects.exclude(
            subdivision_slug__in=seen_slugs
        ).delete()

    return {
        "total_features": len(features),
        "created_count": created_count,
        "updated_count": updated_count,
        "deleted_count": deleted_count,
    }


def parse_warning_codes(raw_value):
    return [
        code.strip()
        for code in str(raw_value or "").split(",")
        if code and code.strip()
    ]


def warning_labels(raw_value):
    labels = []
    seen = set()

    for code in parse_warning_codes(raw_value):
        if code == "1":
            continue

        label = WARNING_CODE_LABELS.get(code, f"Warning code {code}")
        if label in seen:
            continue

        seen.add(label)
        labels.append(label)

    return labels


def severity_meta(color_code):
    try:
        code = int(color_code)
    except (TypeError, ValueError):
        code = 1

    base_meta = SEVERITY_META.get(code, SEVERITY_META[1])
    return {
        "code": code,
        "label": base_meta["label"],
        "hex": base_meta["hex"],
        "rank": base_meta["rank"],
    }


def build_day_details(properties, day_number):
    warning_value = properties.get(f"Day_{day_number}", "")
    labels = warning_labels(warning_value)
    severity = severity_meta(properties.get(f"Day{day_number}_Color", 1))

    return {
        "day": day_number,
        "warning_codes": parse_warning_codes(warning_value),
        "warning_labels": labels,
        "warning_summary": labels or ["No Warning"],
        "severity": severity,
        "distribution": properties.get(f"dist{day_number}", "") or "",
        "probability": properties.get(f"prob{day_number}", "") or "",
        "has_warning": bool(labels),
    }


def build_available_days(source_date):
    items = []
    for day_number in range(1, 8):
        label = f"Day {day_number}"
        if source_date:
            target_date = source_date + timedelta(days=day_number - 1)
            label = f"Day {day_number} - {target_date.strftime('%b %d, %Y')}"
        items.append({"value": day_number, "label": label})
    return items


def build_feature_collection(alerts):
    alerts = list(alerts)
    source_date = next((alert.source_date for alert in alerts if alert.source_date), None)
    synced_at = next(
        (alert.synced_at for alert in alerts if alert.synced_at),
        None,
    )

    features = []
    for alert in alerts:
        day_details = {
            str(day_number): build_day_details(alert.properties, day_number)
            for day_number in range(1, 8)
        }
        features.append(
            {
                "type": "Feature",
                "geometry": alert.geometry,
                "properties": {
                    "subdivision_name": alert.subdivision_name,
                    "subdivision_slug": alert.subdivision_slug,
                    "source_date": alert.source_date.isoformat()
                    if alert.source_date
                    else "",
                    "source_updated_at": alert.source_updated_at.isoformat()
                    if alert.source_updated_at
                    else "",
                    "lat": alert.properties.get("lat"),
                    "lon": alert.properties.get("lon"),
                    "day_details": day_details,
                },
            }
        )

    from alertsapp.models import SubdivisionAlertImage
    images = SubdivisionAlertImage.objects.all()
    image_dict = {str(img.day_number): img.image.url for img in images if img.image}

    return {
        "type": "FeatureCollection",
        "metadata": {
            "source_date": source_date.isoformat() if source_date else "",
            "source_updated_at": synced_at.isoformat()
            if synced_at
            else "",
            "available_days": build_available_days(source_date),
            "legend": [
                {"code": code, "label": meta["label"], "hex": meta["hex"]}
                for code, meta in SEVERITY_META.items()
            ],
            "total_subdivisions": len(features),
            "alert_images": image_dict,
        },
        "features": features,
    }


def fetch_and_save_imd_map_images():
    from playwright.sync_api import sync_playwright
    from django.core.files.base import ContentFile
    from alertsapp.models import SubdivisionAlertImage
    import logging

    logger = logging.getLogger(__name__)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Taller viewport for more bottom space
        page = browser.new_page(viewport={"width": 900, "height": 1050})
        
        page.goto("https://mausam.imd.gov.in/responsive/subDivisionWiseWarningGIS.php", wait_until="networkidle")
        page.wait_for_selector("#chartdiv2", state="visible", timeout=30000)
        
        for day in range(1, 8):
            try:
                radio_selector = f"input[type='radio'][value='{day}']"
                if page.locator(radio_selector).count() > 0:
                    page.locator(radio_selector).click(force=True)
                    page.wait_for_timeout(2000)
                
                # Aggressively hide the leaflet controls and custom buttons JUST for the screenshot
                page.evaluate("""
                    const hideSelectors = [
                        '.leaflet-control-container',
                        '.leaflet-top',
                        '.leaflet-bottom',
                        '.leaflet-control',
                        '.form-check',
                        '.switch',
                        'button'
                    ];
                    window.hiddenElementsForScreenshot = [];
                    
                    hideSelectors.forEach(sel => {
                        document.querySelectorAll(sel).forEach(el => {
                            if(el && el.style.display !== 'none') {
                                window.hiddenElementsForScreenshot.push({el: el, display: el.style.display});
                                el.style.display = 'none';
                            }
                        });
                    });
                """)
                
                # Take the screenshot using the exact crop coordinates provided by the user
                clip_box = {
                    "x": 123,
                    "y": 728,
                    "width": 682,
                    "height": 796
                }
                screenshot_bytes = page.screenshot(clip=clip_box, full_page=True)

                # Unhide elements
                page.evaluate("""
                    if(window.hiddenElementsForScreenshot) {
                        window.hiddenElementsForScreenshot.forEach(item => {
                            item.el.style.display = item.display;
                        });
                        window.hiddenElementsForScreenshot = [];
                    }
                """)

                import os
                os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
                image_name = f"imd_alert_map_day_{day}.png"
                
                obj, created = SubdivisionAlertImage.objects.get_or_create(day_number=day)
                obj.image.save(image_name, ContentFile(screenshot_bytes), save=True)
                
                if created:
                    logger.info(f"Created new image record for day {day}")
                else:
                    logger.info(f"Updated image record for day {day}")
                    
            except Exception as e:
                logger.error(f"Error fetching map for day {day}: {e}")

        browser.close()


DISTRICT_WISE_URLS = {
    "Andaman and Nicobar Islands": "https://mausam.imd.gov.in/imd_latest/contents/districtwise-warning_mc.php?id=34",
    "Andhra Pradesh": "https://mausam.imd.gov.in/imd_latest/contents/districtwise-warning_mc.php?id=2",
    "Arunachal Pradesh": "https://mausam.imd.gov.in/imd_latest/contents/districtwise-warning_mc.php?id=30",
    "Assam": "https://mausam.imd.gov.in/imd_latest/contents/districtwise-warning_mc.php?id=24",
    "Bihar": "https://mausam.imd.gov.in/imd_latest/contents/districtwise-warning_mc.php?id=11",
    "Chandigarh": "https://mausam.imd.gov.in/imd_latest/contents/districtwise-warning_mc.php?id=17",
    "Chhattisgarh": "https://mausam.imd.gov.in/imd_latest/contents/districtwise-warning_mc.php?id=12",
    "Delhi": "https://mausam.imd.gov.in/imd_latest/contents/districtwise-warning_mc.php?id=7",
    "Goa": "https://mausam.imd.gov.in/imd_latest/contents/districtwise-warning_mc.php?id=19",
    "Gujarat": "https://mausam.imd.gov.in/imd_latest/contents/districtwise-warning_mc.php?id=9",
    "Haryana": "https://mausam.imd.gov.in/imd_latest/contents/districtwise-warning_mc.php?id=22",
    "Himachal Pradesh": "https://mausam.imd.gov.in/imd_latest/contents/districtwise-warning_mc.php?id=3",
    "Jammu and Kashmir": "https://mausam.imd.gov.in/imd_latest/contents/districtwise-warning_mc.php?id=18",
    "Jharkhand": "https://mausam.imd.gov.in/imd_latest/contents/districtwise-warning_mc.php?id=15",
    "Karnataka": "https://mausam.imd.gov.in/imd_latest/contents/districtwise-warning_mc.php?id=13",
    "Kerala": "https://mausam.imd.gov.in/imd_latest/contents/districtwise-warning_mc.php?id=4",
    "Ladakh": "https://mausam.imd.gov.in/imd_latest/contents/districtwise-warning_mc.php?id=23",
    "Lakshadweep": "https://mausam.imd.gov.in/imd_latest/contents/districtwise-warning_mc.php?id=4",
    "Madhya Pradesh": "https://mausam.imd.gov.in/imd_latest/contents/districtwise-warning_mc.php?id=29",
    "Maharashtra": "https://mausam.imd.gov.in/imd_latest/contents/districtwise-warning_mc.php?id=21",
    "Manipur": "https://mausam.imd.gov.in/imd_latest/contents/districtwise-warning_mc.php?id=33",
    "Meghalaya": "https://mausam.imd.gov.in/imd_latest/contents/districtwise-warning_mc.php?id=6",
    "Mizoram": "https://mausam.imd.gov.in/imd_latest/contents/districtwise-warning_mc.php?id=31",
    "Nagaland": "https://mausam.imd.gov.in/imd_latest/contents/districtwise-warning_mc.php?id=32",
    "Odisha": "https://mausam.imd.gov.in/imd_latest/contents/districtwise-warning_mc.php?id=10",
    "Puducherry": "https://mausam.imd.gov.in/imd_latest/contents/districtwise-warning_mc.php?id=26",
    "Punjab": "https://mausam.imd.gov.in/imd_latest/contents/districtwise-warning_mc.php?id=17",
    "Rajasthan": "https://mausam.imd.gov.in/imd_latest/contents/districtwise-warning_mc.php?id=8",
    "Sikkim": "https://mausam.imd.gov.in/imd_latest/contents/districtwise-warning_mc.php?id=20",
    "Tamil Nadu": "https://mausam.imd.gov.in/imd_latest/contents/districtwise-warning_mc.php?id=26",
    "Telangana": "https://mausam.imd.gov.in/imd_latest/contents/districtwise-warning_mc.php?id=1",
    "Tripura": "https://mausam.imd.gov.in/imd_latest/contents/districtwise-warning_mc.php?id=16",
    "Uttar Pradesh": "https://mausam.imd.gov.in/imd_latest/contents/districtwise-warning_mc.php?id=5",
    "Uttarakhand": "https://mausam.imd.gov.in/imd_latest/contents/districtwise-warning_mc.php?id=14",
    "West Bengal": "https://mausam.imd.gov.in/imd_latest/contents/districtwise-warning_mc.php?id=28",
}


DISTRICT_CROP_CONFIGS = {
    # Example config: "State Name": (x, y, width, height)
    # Add coordinates here as you find them locally
    # "Andhra Pradesh": (100, 50, 800, 600),
}


def fetch_and_save_district_map_images(target_states=None):
    from playwright.sync_api import sync_playwright
    from django.core.files.base import ContentFile
    from alertsapp.models import DistrictAlertImage
    import logging
    import os
    import io
    from PIL import Image

    logger = logging.getLogger(__name__)

    states_to_process = target_states if target_states else DISTRICT_WISE_URLS.keys()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Standard viewport. Massive viewports cause Playwright cropping issues for wide states.
        page = browser.new_page(viewport={"width": 1920, "height": 1080})
        
        for state_name in states_to_process:
            url = DISTRICT_WISE_URLS.get(state_name)
            if not url:
                continue

            try:
                page.goto(url, wait_until="networkidle")
                page.wait_for_selector("#maindiv", state="visible", timeout=30000)
                page.wait_for_selector("#chartdiv1", state="visible", timeout=30000)
                
                page.wait_for_timeout(1000) # Give AmCharts a second to redraw
                
                for day in range(1, 6):
                    try:
                        radio_selector = f"input[type='radio'][value='Day_{day}']"
                        if page.locator(radio_selector).count() > 0:
                            page.locator(radio_selector).click(force=True)
                            
                        # Wait a little for the map to fully render
                        page.wait_for_timeout(2000)
                        
                        # ULTIMATE UNCLIP LOGIC: Remove all clip-paths and force overflow visible
                        # This prevents AmCharts from mathematically slicing wide/tall states
                        # Also hide all overlapping UI elements (headers, navbars) and container borders
                        page.evaluate("""
                            document.querySelectorAll('*').forEach(el => {
                                if (el.hasAttribute('clip-path')) {
                                    el.removeAttribute('clip-path');
                                }
                                const style = window.getComputedStyle(el);
                                if (style.overflow === 'hidden' || style.overflow === 'clip') {
                                    el.style.setProperty('overflow', 'visible', 'important');
                                }
                            });
                            
                            // Hide UI elements that might overlap the map when overflow is visible
                            document.querySelectorAll('header, footer, nav, .header, .navbar, .top-nav, .footer, iframe').forEach(el => {
                                if (el) el.style.setProperty('display', 'none', 'important');
                            });
                            
                            // Remove borders on containers that might draw over the overflowing map
                            document.querySelectorAll('#maindiv, #chartdiv1, .container, .row').forEach(el => {
                                if (el) {
                                    el.style.setProperty('border', 'none', 'important');
                                    el.style.setProperty('box-shadow', 'none', 'important');
                                    el.style.setProperty('background', 'transparent', 'important');
                                }
                            });
                            
                            document.body.style.background = 'transparent';
                        """)
                        
                        # Give AmCharts time to respond
                        page.wait_for_timeout(1000)
                        
                        # Smart crop using the SVG group element
                        svgelements = page.query_selector_all("svg")
                        if len(svgelements) > 1:
                            svg = svgelements[1]
                        elif len(svgelements) == 1:
                            svg = svgelements[0]
                        else:
                            raise Exception("No SVG found")

                        svg_box = svg.bounding_box()
                        svg_area = svg_box['width'] * svg_box['height']
                        
                        best_g = None
                        best_area = 0
                        
                        for g in svg.query_selector_all("g"):
                            box = g.bounding_box()
                            if not box:
                                continue
                            area = box['width'] * box['height']
                            if area > best_area and area < (svg_area * 0.95):
                                best_area = area
                                best_g = g
                                
                        if not best_g:
                            raise Exception("Could not find suitable map group inside SVG")
                            
                        buffer = io.BytesIO()
                        buffer.write(best_g.screenshot(omit_background=True))
                        buffer.seek(0)
                        final_bytes = buffer.read()

                        os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
                        
                        obj, created = DistrictAlertImage.objects.get_or_create(
                            state_name=state_name, 
                            day_number=day
                        )
                            
                        image_name = f"district_alert_{state_name.replace(' ', '_')}_day_{day}.png"
                        obj.image.save(image_name, ContentFile(final_bytes), save=True)
                        
                        action = "Created" if created else "Updated"
                        logger.info(f"{action} image record for {state_name} day {day}")
                            
                    except Exception as e:
                        logger.error(f"Error fetching district map for {state_name} day {day}: {e}")
                        
            except Exception as e:
                logger.error(f"Error loading URL for {state_name}: {e}")

        browser.close()



