# WeatherApp 🌤️

## Overview
WeatherApp is a personal weather portal built with **Django** and **MySQL**. It provides Indian users with real‑time weather data, 5‑day forecasts, hourly updates, and region‑specific weather news. The site is designed for simplicity, speed, and easy extensibility.

## Core Features
- **Current Weather** – Live temperature, humidity, wind, and condition icons for any Indian city.
- **5‑Day Forecast** – Daily high/low, precipitation chance, and summary.
- **Hourly Updates** – Fine‑grained hourly view for short‑term planning.
- **News Feed** – Aggregated weather news; initially focused on Kerala, with plans to expand nationwide.
- **Responsive UI** – Clean, mobile‑first design using vanilla CSS and JavaScript.

## Planned Enhancements
- **Weather Alerts** – Push red‑alert emails and in‑app notifications for severe weather.
- **Nowcast Map** – Real‑time alert overlay on an interactive map.
- **National & State Coverage** – Extend news and forecasts to all Indian states.
- **Community Stories** – Let users share weather experiences and photos.

## Installation & Setup
1. **Clone the repo**
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
   ```
4. **Configure the database**
   - Install MySQL and start the service.
   - Create a database (e.g., `weatherapp`).
   - Copy `.env.example` to `.env` and fill in `DB_NAME`, `DB_USER`, `DB_PASSWORD`, etc.
5. **Run migrations**
   ```bash
   python manage.py migrate
   ```
6. **Start the development server**
   ```bash
   python manage.py runserver
   ```
   Visit `http://127.0.0.1:8000/` in your browser.

## Docker Deployment (Production)
We ship a multi‑stage Docker build ready for production:
```bash
docker compose up -d --build
```
The container runs **Gunicorn** behind **WhiteNoise** for efficient static file handling and uses **Redis** for caching and Celery task queues.

## Contributing
This project is primarily personal, but contributions are welcome:
- Open an issue for bugs or feature ideas.
- Submit a pull request with clear commit messages.

## License
MIT License – feel free to fork and adapt.

## Acknowledgements
- **Django** – the powerful web framework.
- **MySQL** – reliable relational database.
- **Gunicorn** – WSGI HTTP server for production.
- **WhiteNoise** – static file serving.
- **Redis** – caching and Celery broker.
