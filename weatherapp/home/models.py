from django.db import models

from home.utils import join_place_parts, normalize_place_name, normalize_whitespace, state_slug


class UserSettings(models.Model):
    visitor_id = models.CharField(max_length=64, unique=True, db_index=True)
    city = models.CharField(max_length=120, default="")
    country = models.CharField(max_length=120)
    state = models.CharField(max_length=120)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "User Settings"
        verbose_name_plural = "User Settings"

    def __str__(self):
        return self.home_location_label

    @property
    def state_slug(self):
        return state_slug(self.state)

    @property
    def home_location_label(self):
        return join_place_parts(self.city, self.state, self.country)

    def save(self, *args, **kwargs):
        self.city = normalize_place_name(self.city)
        self.country = normalize_place_name(self.country)
        self.state = normalize_place_name(self.state)
        super().save(*args, **kwargs)
