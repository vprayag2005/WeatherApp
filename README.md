# Clima - Indian Weather Portal

## Overview

Clima is a comprehensive weather portal designed specifically for users in India. Built with Django, it provides a centralized platform to track real-time weather conditions, forecasts, and official severe weather warnings across the country. 

The project aims to take raw, often hard-to-read meteorological data (such as official warnings from the India Meteorological Department) and present it in a highly visual, easy-to-understand, and modern dark-themed interface.

## Core Features

- **Personalized Dashboard**
  Users can save their location settings to automatically receive weather data and regional news tailored to their specific state and city.

- **Real-Time Weather & Forecasts**
  Search for any city to view current conditions (temperature, humidity, wind), along with detailed 5-day forecasts and hourly breakdowns for short-term planning.

- **Official IMD Weather Alerts**
  The platform integrates directly with the India Meteorological Department (IMD) to provide up-to-date severe weather warnings.
  - **Statewise Alerts:** View color-coded subdivision warnings across India.
  - **Districtwise Alerts:** Inspect detailed, interactive maps highlighting specific weather warnings (heavy rain, heatwaves, etc.) down to the district level for the next 5 days.

- **Aggregated News Feed**
  Stay informed with a curated weather and climate news feed, filtered by Global, National, and Regional scopes based on your saved location.

- **Premium UI / UX**
  The interface is built with a mobile-first approach, featuring a custom dark mode, glassmorphism design elements, and smooth micro-animations to make weather tracking an enjoyable visual experience.

## Technical Stack

- **Backend:** Python, Django
- **Database:** MySQL
- **Background Processing:** Celery & Redis (used for asynchronously syncing heavy map data from official sources)
- **Scraping:** Playwright (used to render and capture complex mapping layers)
- **Deployment:** Docker, Docker Compose, Gunicorn, WhiteNoise

## Installation & Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/vprayag2005/WeatherApp.git
   cd WeatherApp
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```

4. **Configure the database**
   - Install MySQL and ensure the service is running.
   - Create a database (e.g., `weatherapp`).
   - Copy `.env.example` to `.env` and fill in your database credentials.

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Start the development server**
   ```bash
   python manage.py runserver
   ```
   You can now visit `http://127.0.0.1:8000/` in your browser.

## Docker Deployment (Production)

For production deployment, the project includes a multi-stage Docker setup that runs the Django application (via Gunicorn), the Celery worker for background tasks, and a Redis message broker.

```bash
docker compose up -d --build
```


