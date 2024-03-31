from django.urls import path
from .views import *

urlpatterns = [
    path('scraped-data/', scrape_and_display, name='scraped-data'),#endpoint to get and check data 

]
