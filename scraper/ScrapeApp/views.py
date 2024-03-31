from django.shortcuts import render
from .utils import scrape_subway_stores,calculate_catchment
from .models import *  
from django.http import JsonResponse
import googlemaps,spacy,re
from datetime import datetime
from django.conf import settings
import nltk
from django.db.models import Max
from nltk.tokenize import word_tokenize

nltk.download('punkt')

api_key = settings.GOOGLE_MAPS_API_KEY
gmaps = googlemaps.Client(key=settings.GOOGLE_MAPS_API_KEY)

def scrape_and_display(request):
    # Call the scraping function
    scrape_subway_stores()

    # Fetch scraped data from your Django model and pass it to the template
    scraped_data = Store.objects.all()
    return render(request, 'scraped_data.html', {'scraped_data': scraped_data})





def get_coordinates_api(request):
    if request.method == 'GET':
        # Retrieve all addresses from the Store model
        stores = Store.objects.all()
        
        # List to store coordinates for all addresses
        all_coordinates = []

        for store in stores:
            # Geocode the address using Google Maps Geocoding API
            geocode_result = gmaps.geocode(store.address)

            if geocode_result:
                # If geocoding is successful, extract latitude and longitude
                latitude = geocode_result[0]['geometry']['location']['lat']
                longitude = geocode_result[0]['geometry']['location']['lng']
                coordinates = {'latitude': latitude, 'longitude': longitude}
                all_coordinates.append(coordinates)
            else:
                # If geocoding fails for any address, skip it
                print(f"Geocoding failed for address: {store.address}")

        return JsonResponse({'all_coordinates': all_coordinates}, status=200)
    else:
        # Handle other HTTP methods
        return JsonResponse({'error': 'Only GET method is allowed'}, status=405)
    
from math import sin, cos, radians

def calculate_catchment(latitude, longitude, radius):
    # Earth radius in kilometers
    earth_radius = 6371.0

    # Convert latitude and longitude to radians
    lat_radians = radians(latitude)
    lng_radians = radians(longitude)

    # Calculate points for the circle
    points = []
    for angle in range(0, 360, 10):
        # Convert angle to radians
        angle_rad = radians(angle)

        # Calculate new latitude and longitude for the point on the circle
        new_latitude = latitude + (radius / earth_radius) * sin(angle_rad)
        new_longitude = longitude + (radius / (earth_radius * cos(lat_radians))) * cos(angle_rad)

        points.append((new_latitude, new_longitude))
    return points



def visualize_outlets(request):
    if request.method == 'GET':
        selected_outlet_id = request.GET.get('outlets')

        if selected_outlet_id:
            # Fetch the selected outlet from the database
            selected_outlet = Store.objects.get(id=selected_outlet_id)

            # Fetch all outlets within a 5km radius of the selected outlet
            outlets_within_5km = Store.objects.filter(
                latitude__isnull=False,
                longitude__isnull=False
            ).exclude(id=selected_outlet_id).filter(
                latitude__range=(selected_outlet.latitude - 0.045, selected_outlet.latitude + 0.045),
                longitude__range=(selected_outlet.longitude - 0.045, selected_outlet.longitude + 0.045)
            )

            # Prepare data for rendering on the map
            outlet_data = []
            for outlet in outlets_within_5km:
                outlet_data.append({
                    'name': outlet.store_name,
                    'id': outlet.id,
                    'latitude': outlet.latitude,
                    'longitude': outlet.longitude,
                    'catchment': calculate_catchment(outlet.latitude, outlet.longitude, 5)  
                })

            return render(request, 'outlets_map.html', {'outlets': outlet_data, 'api_key': api_key})

    # Fetch all outlets from the database if no outlet is selected or if the method is not GET
    outlets = Store.objects.all()

    # Prepare data for rendering on the map
    outlet_data = []
    for outlet in outlets:
        if outlet.latitude and outlet.longitude:
            outlet_data.append({
                'name': outlet.store_name,
                'id':outlet.id,
                'address':outlet.address,
                'latitude': outlet.latitude,
                'longitude': outlet.longitude,
                'waze':outlet.waze_link,
                'catchment': calculate_catchment(outlet.latitude, outlet.longitude, 5)  
            })

    return render(request, 'outlets_map.html', {'outlets': outlet_data, 'api_key': api_key})

def extract_closing_time(operating_hours):
    # Regular expressions to match different formats of closing time
    patterns = [
        r'(\d{1,2}:\d{2} [AP]M)',  # Matches hours:minutes AM/PM format
        r'(\d{1,2} [AP]M)',         # Matches hours AM/PM format
        r'(\d{1,2}:\d{2})',         # Matches hours:minutes format
        r'(\d{1,2})'                # Matches hours format
    ]

    # Iterate over the regular expressions
    for pattern in patterns:
        match = re.search(pattern, operating_hours)
        if match:
            closing_time_str = match.group(0)
            closing_time = datetime.strptime(closing_time_str, '%I:%M %p') if ':' in closing_time_str else \
                           datetime.strptime(closing_time_str + ' PM', '%I %p') if 'AM' not in closing_time_str else \
                           datetime.strptime(closing_time_str + ' AM', '%I %p')
            print(closing_time)
            return closing_time.time()

    return None


def get_latest_closing_store():
    # Get the latest closing time from the OperatingHours model
    latest_closing_time = OperatingHours.objects.aggregate(latest_closing=Max('closing_time'))['latest_closing']
    # Get the store associated with the latest closing time
    latest_store = Store.objects.filter(operatinghours__closing_time=latest_closing_time).first()
    return latest_store

def count_outlets_in_area(area):
    # Count the number of outlets located in the specified area
    num_area_outlets = Store.objects.filter(address__icontains=area.capitalize()).count()
    return f"There are {num_area_outlets} outlets located in {area.capitalize()}."


def search_outlets(request):
    if request.method == 'GET':
        # Get the user's query from the request
        query = request.GET.get('query', '')
        
        # Process the query using NLTK
        response = handle_query(query)
        
        # Return the response as JSON
        return JsonResponse({'response': response}, status=200)
    else:
        # Handle other HTTP methods
        return JsonResponse({'error': 'Only GET method is allowed'}, status=405)
    
def get_outlets_with_latest_closing():
    # Get closing times and corresponding store IDs from OperatingHours, excluding entries where the closing time is "Closed"
    closing_times_and_stores = OperatingHours.objects.exclude(closing_time__iexact="Closed").values_list('closing_time', 'store_id')
    print(closing_times_and_stores)

    # Extract closing times from the queryset
    closing_times = [entry[0].strip() for entry in closing_times_and_stores]

    # Extract time part from the closing times and convert to total minutes for comparison
    closing_times_numeric = []
    for time in closing_times:
        # Split the time string by ':'
        time_parts = time.split(':')
        # Check if the time string is formatted correctly and has at least two parts
        if len(time_parts) >= 2:
            # Convert the hours and minutes to total minutes for comparison
            closing_times_numeric.append(int(time_parts[0]) * 60 + int(time_parts[1]))
        else:
            # Handle incorrectly formatted time strings (optional)
            print(f"Warning: Incorrect time format found - {time}")

    if closing_times_numeric:
        # Find the largest closing time
        largest_closing_time_minutes = max(closing_times_numeric)

        # Find the index of the largest closing time
        largest_index = closing_times_numeric.index(largest_closing_time_minutes)

        # Get the corresponding store ID from the queryset
        corresponding_store_id = closing_times_and_stores[largest_index][1]

        print("Corresponding Store ID:", corresponding_store_id)
        # Get the store name corresponding to the store ID
        store_name = Store.objects.get(id=corresponding_store_id).store_name
        return f"{store_name} closes the latest"
    else:
        print("No valid closing times found")





def handle_query(query):
    # Tokenize the user query using NLTK
    tokens = word_tokenize(query.lower())
    
    # Check for specific keywords related to the query
    relevant_keywords = ['latest', 'closes', 'store']
    if any(keyword in tokens for keyword in relevant_keywords):
        return get_outlets_with_latest_closing()
    
    # Check if the query contains common location words
    area = None
    common_areas = ['bangsar', 'cheras', 'ampang', 'bukit jalil', 'setapak', 'kuala lumpur']
    for token in tokens:
        if token in common_areas:
            area = token
            break
    
    if area:
        return count_outlets_in_area(area)
    else:
        return "Sorry, I couldn't understand your query or the specified area is not supported."