from django.shortcuts import render
from .utils import scrape_subway_stores
from .models import Store  
from django.http import JsonResponse

def scrape_and_display(request):
    # Call the scraping function
    scrape_subway_stores()

    # Fetch scraped data from your Django model and pass it to the template
    scraped_data = Store.objects.all()
    return render(request, 'scraped_data.html', {'scraped_data': scraped_data})

