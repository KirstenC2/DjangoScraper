from django.urls import path
from .views import *

urlpatterns = [
    path('api/scraped_data/', scrape_and_display, name='scraped_data'),
    path('api/get_coordinates/', get_coordinates_api, name='get_coordinates_api'),
    path('', visualize_outlets, name='outlets_map'),
    path('search_outlets/', search_outlets, name='search_outlets'),  
]
