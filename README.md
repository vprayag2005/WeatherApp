# Weather Website

## Overview
This is a personal weather website developed using Django and MySQL, designed to provide users with accurate and up-to-date weather information. The website focuses on India, specifically offering detailed weather forecasts and news updates.

## Features
- **Current Weather**: Displays real-time weather conditions for various locations.
- **5-Day Weather Forecast**: Provides users with a detailed forecast for the upcoming five days.
- **Hourly Weather**: Offers hourly updates for accurate planning.
- **News**: Includes global, national, and region-specific weather news. Currently, only Kerala news is included, with plans to expand to other states.

## Future Features
- **Weather Alerts**: Implement alerts for severe weather conditions, including red alerts sent to user emails.
- **Nowcast**: Display weather alerts on a map for real-time updates.
- **National and Regional Weather**: Expand the coverage to include more states.
- **User Experience Sharing**: Allow users to post their weather experiences and share content.

## Installation
1. Clone the repository:
   ```bash
   git clone <https://github.com/vprayag2005/WeatherApp.git>
   ```
2. Navigate to the project directory:
   ```bash
   cd <project-directory>
   ```
3. Set up your virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```
4. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```
5. Set up the database:
   - Ensure you have MySQL installed and running.
   - Create a database and update the database settings in `settings.py`.
   - Run migrations:
     ```bash
     python manage.py migrate
     ```

## Usage
- Run the development server:
  ```bash
  python manage.py runserver
  ```
- Access the website at `http://127.0.0.1:8000/`.

## Contributing
This project is a personal project and is not open source. However, you can raise issues and provide feedback if you encounter any problems or have suggestions.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgements
- [Django](https://www.djangoproject.com/) - The web framework used.
- [MySQL](https://www.mysql.com/) - The database used.
