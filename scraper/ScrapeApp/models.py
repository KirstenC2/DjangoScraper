from django.db import models
from geopy.geocoders import Nominatim

class Store(models.Model):
    store_name = models.CharField(max_length=255)
    address = models.TextField()
    latitude = models.FloatField(blank=True, null=True)  # Allow null values for coordinates
    longitude = models.FloatField(blank=True, null=True)  # Allow null values for coordinates
    waze_link = models.URLField(blank=True, null=True)  # Optional field for Waze link
    
    def __str__(self):
        return self.store_name

    def save(self, *args, **kwargs):
        if not self.latitude or not self.longitude:
            geolocator = Nominatim(user_agent="store_locator")
            location = geolocator.geocode(self.address)
            if location:
                self.latitude = location.latitude
                self.longitude = location.longitude
        super().save(*args, **kwargs)

class OperatingHours(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    day = models.CharField(max_length=20)
    opening_time = models.CharField(max_length=10)
    closing_time = models.CharField(max_length=10)