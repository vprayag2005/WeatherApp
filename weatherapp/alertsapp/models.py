from django.db import models
from django.utils.text import slugify


class SubdivisionAlert(models.Model):
    subdivision_name = models.CharField(max_length=140, unique=True)
    subdivision_slug = models.SlugField(max_length=160, unique=True)
    source_date = models.DateField(null=True, blank=True)
    source_updated_at = models.DateTimeField(null=True, blank=True)
    geometry = models.JSONField(default=dict, blank=True)
    properties = models.JSONField(default=dict, blank=True)
    synced_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("subdivision_name",)

    def __str__(self):
        return self.subdivision_name

    def save(self, *args, **kwargs):
        if self.subdivision_name and not self.subdivision_slug:
            self.subdivision_slug = slugify(self.subdivision_name)
        super().save(*args, **kwargs)


class SubdivisionAlertImage(models.Model):
    day_number = models.IntegerField(unique=True)
    image = models.ImageField(upload_to="alert_images/")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("day_number",)

    def __str__(self):
        return f"Day {self.day_number} Map Image"


class DistrictAlertImage(models.Model):
    state_name = models.CharField(max_length=100)
    day_number = models.IntegerField()
    image = models.ImageField(upload_to="district_alert_images/")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("state_name", "day_number")
        unique_together = ("state_name", "day_number")

    def __str__(self):
        return f"{self.state_name} - Day {self.day_number} Map Image"



