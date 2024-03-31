from django.db import models


class Store(models.Model):
    store_name = models.CharField(max_length=255)
    address = models.TextField()
    latitude = models.FloatField(blank=True, null=True)  # Allow null values for coordinates
    longitude = models.FloatField(blank=True, null=True)  # Allow null values for coordinates
    waze_link = models.URLField(blank=True, null=True)  # Optional field for Waze link
    operating_hours = models.TextField(blank=True, null=True)  # Field to store operating hours text

    def __str__(self):
        return self.store_name
    