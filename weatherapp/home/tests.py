from unittest.mock import Mock, patch

from django.test import TestCase
from django.urls import reverse

from home.models import UserSettings


class UserSettingsFlowTests(TestCase):
    def test_first_time_user_is_redirected_to_settings(self):
        response = self.client.get(reverse("home"))

        self.assertRedirects(response, reverse("settings"))
        self.assertIn("visitor_id", response.cookies)

    def test_submitting_settings_unlocks_home(self):
        self.client.get(reverse("settings"))

        response = self.client.post(
            reverse("settings"),
            data={
                "city": "Chennai",
                "country": "India",
                "state": "Tamil Nadu",
            },
        )

        self.assertRedirects(response, reverse("home"))
        self.assertTrue(
            UserSettings.objects.filter(
                city="Chennai",
                state="Tamil Nadu",
            ).exists()
        )

        home_response = self.client.get(reverse("home"))
        self.assertEqual(home_response.status_code, 200)
        self.assertContains(home_response, "Chennai, Tamil Nadu, India")
        self.assertContains(home_response, 'savedHomeQuery: "Chennai"')

    def test_home_page_loads_saved_city_config_before_weather_script(self):
        self.client.cookies["visitor_id"] = "saved-city-visitor"
        UserSettings.objects.create(
            visitor_id="saved-city-visitor",
            city="Chennai",
            country="India",
            state="Tamil Nadu",
        )

        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        html = response.content.decode()
        self.assertLess(
            html.index("window.weatherConfig = {"),
            html.index("js/script.js"),
        )
        self.assertIn('savedHomeLabel: "Chennai, Tamil Nadu, India"', html)
        self.assertIn('savedHomeQuery: "Chennai"', html)

    def test_city_is_required_in_settings(self):
        self.client.get(reverse("settings"))

        response = self.client.post(
            reverse("settings"),
            data={
                "country": "India",
                "state": "Tamil Nadu",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Please enter your city.")

    def test_regional_news_redirect_uses_saved_state(self):
        self.client.cookies["visitor_id"] = "test-visitor"
        UserSettings.objects.create(
            visitor_id="test-visitor",
            city="Chennai",
            country="India",
            state="Tamil Nadu",
        )

        response = self.client.get(reverse("my_state_news"))
        self.assertRedirects(response, "/news/stateweathernews/tamil-nadu/")

    @patch("home.views.requests.get")
    def test_resolve_location_returns_city_state_and_country(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"name": "Chennai", "state": "Tamil Nadu", "country": "IN"}
        ]
        mock_get.return_value = mock_response

        response = self.client.post(
            reverse("resolve_location"),
            data={"lat": "13.0827", "lon": "80.2707"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content,
            {
                "city": "Chennai",
                "state": "Tamil Nadu",
                "country": "India",
                "label": "Chennai, Tamil Nadu, India",
            },
        )
