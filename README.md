# DjangoScraper

# Building Django Project
## Step 1: Build a Django project
django-admin startproject {project_name}

## Step 2: Create an App
cd {project_name}
python manage.py startapp {app_name}

## Step 3: Make migrations upon changes and updates
python manage.py makemigrations
python manage.py migrate

## Step 4: create a superuser who can monitor the website
python manage.py createsuperuser

# DjangoScraper detailes

## Database
using the sqlite3, and file is being stored in the repo

## Django App
Name: ScrapeApp

### Models
#### Store
storing all the geographical or locations related information
(store_name,address,latitude,longitude,waze_link)

#### OperatingHours
storing all the operating hours of each branches
(store - foreign key, day, opening_time, closing_time)

### Views
Most of the functions are located here
#### Scraping data and display on a html
- scrape_and_display

#### Get all geographical coordinated of all stores
- get_coordinates_api

#### Calculate stores within 5km radius 
- calculate_catchment

#### Main Page to present all
- visualize_outlets


#### NLP to handle query from user
- get_latest_closing_store
- get_outlets_with_latest_closing
- extract_closing_time
- search_outlets
- handle_query


### Utils
This file is to serve as a helper function that handling most of the scraping logic
- scrape_subway_stores
- calculate_catchment

### Urls
This file has all the api link serves in

### requirement.txt 
includes all the required library

# Deployment to AWS EC2 
- Start an instance
- Configure the instance
- Public IP address : 13.230.7.221
- Setup Inboud Rules for connection port 8000
- Get into the Server
- Clone from git 
- install all the required packages
- Run the server to serve the Django project 
- Connect through the link (http://13.230.7.221:8000/outlets_map/)
this will show the page with scraped data, and other fuunctionality