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

from .models import Store
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from bs4 import BeautifulSoup
import unicodedata
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

        # Extracting operating hours
        operating_hours_element = location_element.select_one('.infoboxcontent p:nth-of-type(3)')
        operating_hours = operating_hours_element.text.strip() if operating_hours_element else ""

        store_data.append({
            'store_name': store_name,
            'address': address,
            'latitude': latitude,
            'longitude': longitude,
            'waze_link': waze_link,
            'operating_hours': operating_hours
        })

    return store_data



def save_data_to_model(df):
    for index, row in df.iterrows():
        Store.objects.create(
            store_name=row['store_name'],
            address=row['address'],
            latitude=row['latitude'],
            longitude=row['longitude'],
            waze_link=row['waze_link'],
            operating_hours=row['operating_hours']
        )

