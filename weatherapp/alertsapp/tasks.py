from celery import shared_task

from alertsapp.services import sync_subdivision_alerts, fetch_and_save_imd_map_images


@shared_task
def sync_subdivision_alerts_task():
    result = sync_subdivision_alerts()
    print(f"Subdivision alert sync completed: {result}")
    
    print("Fetching IMD map images via Playwright...")
    try:
        fetch_and_save_imd_map_images()
        print("IMD map images fetched successfully.")
    except Exception as e:
        print(f"Error fetching IMD map images: {e}")
        
    return result


@shared_task
def sync_district_alerts_task():
    from alertsapp.services import fetch_and_save_district_map_images
    print("Fetching IMD district map images via Playwright...")
    try:
        fetch_and_save_district_map_images()
        print("IMD district map images fetched successfully.")
    except Exception as e:
        print(f"Error fetching IMD district map images: {e}")
        
    return True

