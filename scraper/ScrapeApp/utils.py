# # ScrapeApp/utils.py

# from .models import ScrapedData
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.service import Service
# from webdriver_manager.chrome import ChromeDriverManager
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# import pandas as pd
# from bs4 import BeautifulSoup
# import unicodedata


# def scrape_subway_stores():
#     # Set up Chrome options for headless mode
#     chrome_options = Options()
#     chrome_options.add_argument("--headless")

#     # Initialize Selenium WebDriver using WebDriverManager
#     service = Service(ChromeDriverManager().install())
#     driver = webdriver.Chrome(service=service, options=chrome_options)

#     try:
#         # Navigate to the website
#         driver.get('https://subway.com.my/find-a-subway')

#         # Input "Kuala Lumpur" into the search field
#         search_input = WebDriverWait(driver, 10).until(
#             EC.presence_of_element_located((By.ID, "fp_searchAddress"))
#         )
#         search_input.send_keys("Kuala Lumpur")

#         # Click on the search button
#         search_button = WebDriverWait(driver, 10).until(
#             EC.element_to_be_clickable((By.ID, "fp_searchAddressBtn"))
#         )
#         search_button.click()

#         # Wait for the page to reload with search results
#         WebDriverWait(driver, 10).until(
#             EC.presence_of_element_located((By.ID, "fp_locationlist"))
#         )

#         # Extract HTML content
#         html_content = driver.page_source

#         # Parse HTML content with BeautifulSoup
#         soup = BeautifulSoup(html_content, 'html.parser')

#         # Extract store information
#         store_data = []
#         location_list_elements = soup.find_all(class_='fp_listitem')
#         for location_element in location_list_elements:
#             store_name = location_element.find('h4').text.strip()
#             address_element = location_element.select_one('.infoboxcontent p:nth-of-type(1)')
#             address = address_element.text.strip() if address_element else ""
#             latitude = location_element['data-latitude']
#             longitude = location_element['data-longitude']
#             waze_link = location_element.select_one('a[href*="waze.com"]').get('href')

#             # Extracting operating hours
#             operating_hours_element = location_element.select_one('.infoboxcontent p:nth-of-type(3)')
#             operating_hours = unicodedata.normalize("NFKD", operating_hours_element.text.strip()) if operating_hours_element else ""

#             store_data.append({
#                 'store_name': store_name,
#                 'address': address,
#                 'latitude': latitude,
#                 'longitude': longitude,
#                 'waze_link': waze_link,
#                 'operating_hours': operating_hours
#             })

#         # Create DataFrame from the extracted data
#         df = pd.DataFrame(store_data)


#         # Save scraped data to your Django model
#         for index, row in df.iterrows():
#             ScrapedData.objects.create(
#                 store_name=row['store_name'],
#                 address=row['address'],
#                 latitude=row['latitude'],
#                 longitude=row['longitude'],
#                 waze_link=row['waze_link'],
#                 operating_hours=row['operating_hours']
#             )

#     finally:
#         # Close the Selenium WebDriver
#         driver.quit()

from .models import *
from django.db.models import Value, IntegerField
from django.db.models.functions import Cast
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from bs4 import BeautifulSoup
import unicodedata,re
from selenium.common.exceptions import NoSuchElementException


def scrape_subway_stores():
    # Set up Chrome options for headless mode
    chrome_options = Options()
    chrome_options.add_argument("--headless")

    # Initialize Selenium WebDriver using WebDriverManager
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        # Navigate to the website
        driver.get('https://subway.com.my/find-a-subway')

        # Input "Kuala Lumpur" into the search field
        search_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "fp_searchAddress"))
        )
        search_input.send_keys("Kuala Lumpur")

        # Click on the search button
        search_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "fp_searchAddressBtn"))
        )
        search_button.click()

        # Scraping and handling pagination
        scrape_and_handle_pagination(driver)

    finally:
        # Close the Selenium WebDriver
        driver.quit()


def scrape_and_handle_pagination(driver):
    while True:
        # Wait for the page to reload with search results
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "fp_locationlist"))
        )

        # Extract HTML content
        html_content = driver.page_source

        # Parse HTML content with BeautifulSoup
        soup = BeautifulSoup(html_content, 'lxml')

        # Extract store information
        store_data = extract_store_data(soup)

        # Create DataFrame from the extracted data
        df = pd.DataFrame(store_data)

        # Save scraped data to your Django model
        save_data_to_model(df)

        try:
            # Check if there is a next page
            next_button = driver.find_element(By.CLASS_NAME, 'next')
            if 'disabled' in next_button.get_attribute('class'):
                break  # Break the loop if there's no next page
            else:
                next_button.click()  # Click on the next page button
        except NoSuchElementException:
            break  # Break the loop if there's no next page button


def extract_store_data(soup):
    store_data = []
    location_list_elements = soup.find_all(class_='fp_listitem')
    for location_element in location_list_elements:
        store_name = location_element.find('h4').text.strip()
        address_element = location_element.select_one('.infoboxcontent p:nth-of-type(1)')
        address = address_element.text.strip() if address_element else ""
        latitude = location_element['data-latitude']
        longitude = location_element['data-longitude']
        waze_link = location_element.select_one('a[href*="waze.com"]').get('href')

        operating_hours_elements = location_element.select('.infoboxcontent p')[2:-1]
        operating_hours = ' '.join([element.text.strip() for element in operating_hours_elements])

        store_data.append({
            'store_name': store_name,
            'address': address,
            'latitude': latitude,
            'longitude': longitude,
            'waze_link': waze_link,
            'operating_hours': operating_hours
        })

    return store_data

def preprocess_operating_hours(store,entry):
    if "Monday - Sunday" in entry:
        print("this is entry:",entry)
    # Extract the time information using regular expressions
        match = re.search(r'(?:Monday - Sunday|Mon - Sun),\s*(.*?)\s*$', entry)
        if match:
            print("entered",entry)
            time_info = match.group(1)
            # Check if time_info contains opening and closing times
            if "-" in time_info:
                opening_time, closing_time = time_info.split(" - ")
                # Append the time information for each day from Monday to Sunday
                for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]:
                    OperatingHours.objects.create(
                                store=store,
                                day=day,
                                opening_time=opening_time.replace("AM",""),
                                closing_time=closing_time.replace("PM",""),
                            )
            else:
                print("Error: Unexpected format for time_info")
        elif "(" in entry and ")" in entry or "to" in entry:
            print("entered",entry)
            entry = entry.replace(" (", ", ").replace(")", "").replace("to","-").replace("AM"," AM").replace("PM"," PM")
            match = re.search(r'(?:Monday - Sunday|Mon - Sun),\s*(.*?)\s*$', entry)
            time_info = match.group(1)
            if "-" in time_info:
                opening_time, closing_time = time_info.split("-")

                for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]:
                    OperatingHours.objects.create(
                                store=store,
                                day=day,
                                opening_time=opening_time.replace("AM",""),
                                closing_time=closing_time.replace("PM",""),
                            )
            else:
                print("Error: Unexpected format for time_info")
    elif "Mon - Sun" in entry:
        print("Monsun",entry)
        # Split the entry into parts
        entry = entry.replace("Tues"," Tues")
        parts = re.split(r"(\b(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun)\b\s*-\s*\b(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun)\b\s*:\s*|\b[A-Za-z]{3,4}\s*:\s*)", entry)
        print(parts)
        # Extract opening and closing times for weekdays (Mon - Sun)
        weekday_match = re.search(r'(\d{1,2}(?:am|pm))-(\d{1,2}(?:am|pm))', parts[2])
        if weekday_match:
            opening_time = weekday_match.group(1)
            closing_time = weekday_match.group(2)

            for day in ["Monday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]:
                OperatingHours.objects.create(
                                store=store,
                                day=day,
                                opening_time=opening_time.replace("am",""),
                                closing_time=closing_time.replace("pm",""),
                            )

        # Extract opening and closing times for Tuesday
        tuesday_match = re.search(r'Close', parts[4])
        if tuesday_match:
            opening_time = "Closed"
            closing_time = "Closed"
            OperatingHours.objects.create(
                                store=store,
                                day="Tuesday",
                                opening_time=opening_time,
                                closing_time=closing_time,
                            )

    elif "Monday - Friday" in entry and "Saturday & Sunday" in entry:
        print("entered entry", entry)
        parts = re.split(r"(?<=\d[A|P]M) (?=[A-Z])", entry)
        weekday_part = parts[0]
        weekend_part = parts[1]

        # Extract opening time for weekdays
        weekday_match = re.search(r'(?:Monday - Friday|Mon - Fri),\s*(.*?)\s*$', weekday_part)
        if weekday_match:
            weekday_time_info = weekday_match.group(1)
            # Extract opening and closing times for weekdays
            time_match = re.match(r'(\d{1,2}:\d{2}\s*(?:AM|PM))\s*–\s*(\d{1,2}:\d{2}(?:AM|PM))', weekday_time_info)
            if time_match:
                opening_time_weekday = time_match.group(1)
                closing_time_weekday = time_match.group(2)
                for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]:
                    OperatingHours.objects.create(
                                store=store,
                                day=day,
                                opening_time=opening_time_weekday.replace("AM",""),
                                closing_time=closing_time_weekday.replace("PM",""),
                            )
            else:
                print("Error: Unable to match time format for weekdays")

        # Append opening and closing times for weekends
        weekend_match = re.findall(r'\b\d{1,2}:\d{2}\s*[AP]M\b', weekend_part)
        if weekend_match:
            opening_time_weekend = weekend_match[0]
            closing_time_weekend = weekend_match[1]

            OperatingHours.objects.create(
                                store=store,
                                day="Saturday",
                                opening_time=opening_time_weekend.replace("AM",""),
                                closing_time=closing_time_weekend.replace("PM",""),
                            )
            OperatingHours.objects.create(
                                store=store,
                                day="Sunday",
                                opening_time=opening_time_weekend.replace("AM",""),
                                closing_time=closing_time_weekend.replace("PM",""),
                            )
        else:
            print("Error: Unable to match opening and closing time format for weekends")

    else:
        # If "Monday - Sunday" is not mentioned, extract the day and time information separately
        match = re.search(r'([A-Za-z]+)\s*:\s*(.*?)\s*$', entry)
        if match:
            day = match.group(1)
            time_info = match.group(2)
            

def save_data_to_model(df):
    for index, row in df.iterrows():
        # Remove any empty strings from the address
        address_parts = [part.strip() for part in row['address'].split() if part.strip()]
        address = ' '.join(address_parts)
        
        # Check if the address contains "Kuala Lumpur" or "K.L" and if there is at least one space character
        if ("Kuala Lumpur" in address or "K.L" in address) and " " in address:
            store = Store.objects.create(
                store_name=row['store_name'],
                address=address,
                latitude=row['latitude'],
                longitude=row['longitude'],
                waze_link=row['waze_link'],
            )
            # Preprocess operating hours data
            preprocess_operating_hours(store, row['operating_hours'])
            


def calculate_catchment(latitude, longitude):
    """
    Calculate the catchment area around a given latitude and longitude
    by filtering outlets within a 5km radius.
    """
    # Query outlets within 5km radius
    outlets_within_5km = Store.objects.annotate(
        distance=Cast(
            (
                (latitude - Store.latitude) ** 2 +
                (longitude - Store.longitude) ** 2
            ) ** 0.5 * 111.32,  # Approximate distance in kilometers
            output_field=IntegerField()
        )
    ).filter(distance__lte=5)

    return outlets_within_5km
