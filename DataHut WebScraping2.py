# Importing libraries
import random
import time
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
pd.options.mode.chained_assignment = None
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))


# Function to delay some process
def delay():
    time.sleep(random.randint(3, 10))


# Scrolling down the page in order to overcome Lazy Loading
def lazy_loading():
    element = driver.find_element(By.TAG_NAME, 'body')
    count = 0
    while count < 20:
        element.send_keys(Keys.PAGE_DOWN)
        delay()
        count += 1


# Continuously clicking the button to show more products till everything is loaded
def pagination():
    total_number_of_products = driver.find_element(By.XPATH, "//div[@class='css-unii66']/p").text
    total_number_of_products = total_number_of_products.split(' ')
    total_number_of_products = int(total_number_of_products[2])    # Finding the total number of products in the site
    click_count = 0
    while click_count < (total_number_of_products / 60) + 1:  # Since number of products loaded per click is 60
        try:
            lazy_loading()
            driver.find_element(By.XPATH, "//div[@class='css-unii66']/button").click()  # Clicking the button saying
                                                                                        # 'load more products'
            delay()
            click_count += 1
        except:
            click_count += 1
            pass
    lazy_loading()


# Function to fetch the product links of products which are not lazy loaded
def fetch_product_links(all_products_section):
    for product_section in all_products_section.find_all('div', {'class': 'css-foh208'}):
        for product_link in product_section.find_all('a'):
            if product_link['href'].startswith('https:'):
                product_links.append(product_link['href'])
            else:
                product_links.append('https://www.sephora.com' + product_link['href'])


# Function to fetch the product links of products which are lazy loaded
def fetch_lazy_loading_product_links(all_products_section):
    for product_section in all_products_section.find_all('div', {'class': 'css-1qe8tjm'}):
        for product_link in product_section.find_all('a'):
            if product_link['href'].startswith('https:'):
                product_links.append(product_link['href'])
            else:
                product_links.append('https://www.sephora.com' + product_link['href'])


# Function to extract content of the page
def extract_content(url):
    driver.get(url)
    page_content = driver.page_source
    product_soup = BeautifulSoup(page_content, 'html.parser')
    return product_soup


# Function to extract brand name
def brand_data(soup):
    try:
        brand = soup.find('a', attrs={"data-at": "brand_name"}).text
        data['brand'].iloc[product] = brand
    except:
        brand = 'Brand name not available'
        data['brand'].iloc[product] = brand


# Function to extract product name
def product_name(soup):
    try:
        name_of_product = soup.find('span', attrs={"data-at": "product_name"}).text
        data['product_name'].iloc[product] = name_of_product
    except:
        name_of_product = 'Product name not available '
        data['product_name'].iloc[product] = name_of_product


# Function to extract number of reviews
def reviews_data(soup):
    try:
        reviews = soup.find('span', attrs={"data-at": "number_of_reviews"}).text
        data['number_of_reviews'].iloc[product] = reviews
    except:
        reviews = 'Number of reviews not available'
        data['number_of_reviews'].iloc[product] = reviews


# Function to extract number of loves
def love_data(soup):
    try:
        love = soup.find('span', attrs={"class": "css-jk94q9"}).text
        data['love_count'].iloc[product] = love
    except:
        love = 'Love count not available'
        data['love_count'].iloc[product] = love


# Function to extract star rating
def star_data(soup):
    if data['love_count'].iloc[product] != 'Love count not available':            # Since love count and star rating usually coexists
        try:
            star = soup.find('span', attrs={"class": "css-1tbjoxk"})['aria-label']
            data['star_rating'].iloc[product] = star
        except:
            star = 'Star rating not available'
            data['star_rating'].iloc[product] = star


# Function to extract price
def price_data(soup):
    try:
        price = soup.find('b', attrs={"class": "css-0"}).text
        data['price'].iloc[product] = price
    except:
        price = 'Price data not available'
        data['price'].iloc[product] = price


# Function to extract ingredients
def ingredients_data(soup):
    try:
        for ingredient in soup.find('div', attrs={"class": "css-1ue8dmw eanm77i0"}):
            if len(ingredient.contents) == 1:
                try:
                    data['Ingredients'].iloc[product] = ingredient.contents[0].text
                except:
                    data['Ingredients'].iloc[product] = ingredient.contents[0]
            else:
                data['Ingredients'].iloc[product] = ingredient.contents[1]
    except:
        data['Ingredients'].iloc[product] = 'Ingredients data not available'


# To find the element using xpath
def find_element_by_xpath():
    try:
        section = driver.find_element(By.XPATH, "//div[@class='css-32uy52 eanm77i0']").text
        split_sections = section.split('\n')
        return split_sections
    except:
        pass


# Function to extract fragrance family
def fragrance_family():
    split_section = find_element_by_xpath()
    try:
        for feature in split_section:
            key_and_value = feature.split(':')
            try:
                if key_and_value[0] == 'Fragrance Family':
                    data['Fragrance Family'].iloc[product] = key_and_value[1]
            except:
                data['Fragrance Family'].iloc[product] = 'Fragrance family data not available'
    except:
        pass


# Function to extract scent type
def scent_data():
    split_section = find_element_by_xpath()
    try:
        for feature in split_section:
            key_and_value = feature.split(':')
            try:
                if key_and_value[0] == 'Scent Type':
                    data['Scent Type'].iloc[product] = key_and_value[1]
            except:
                data['Scent Type'].iloc[product] = 'Scent type data not available'
    except:
        pass


# Function to extract key notes
def key_notes():
    split_section = find_element_by_xpath()
    try:
        for feature in split_section:
            key_and_value = feature.split(':')
            try:
                if key_and_value[0] == 'Key Notes':
                    data['Key Notes'].iloc[product] = key_and_value[1]
            except:
                data['Key Notes'].iloc[product] = 'Key notes data not available'
    except:
        pass


# Function to extract fragrance description
def fragrance_description():
    split_section = find_element_by_xpath()
    try:
        for feature in split_section:
            key_and_value = feature.split(':')
            try:
                if key_and_value[0] == 'Fragrance Description':
                    data['Fragrance Description'].iloc[product] = key_and_value[1]
            except:
                data['Fragrance Description'].iloc[product] = 'Fragrance description not available'
    except:
        pass


# Function to extract composition
def composition_data():
    split_section = find_element_by_xpath()
    try:
        for feature in split_section:
            key_and_value = feature.split(':')
            try:
                if key_and_value[0].lower() == 'composition':
                    index = split_section.index(feature)
                    data['COMPOSITION'].iloc[product] = split_section[index + 1]
            except:
                data['COMPOSITION'].iloc[product] = 'Composition not available'
    except:
        pass


# Sephora website link
start_url = 'https://www.sephora.com/shop/fragrances-for-women'

driver.get(start_url)

# Continuously clicking the button to show more products till everything is loaded
pagination()

# Converting the content of the page to BeautifulSoup object
content = driver.page_source
homepage_soup = BeautifulSoup(content, 'html.parser')

# Fetching the product links of all items
product_links = []
all_products = homepage_soup.find_all('div', attrs={"class": "css-1322gsb"})[0]
fetch_product_links(all_products)               # Fetching the product links that does not have lazy loading
fetch_lazy_loading_product_links(all_products)  # Fetching the product links that have lazy loading

# Reading the given sample data
sample_df = pd.read_csv('Downloads\\Sephora Sample data - Sheet1.csv')

# Creating a dictionary of the required columns
data_dic = {'product_url': [], 'brand': [], 'product_name': [],
            'number_of_reviews': [], 'love_count': [], 'star_rating': [], 'price': [], 'Fragrance Family': [],
            'Scent Type': [], 'Key Notes': [], 'Fragrance Description': [], 'COMPOSITION': [], 'Ingredients': []}

# Creating a dataframe with those columns
data = pd.DataFrame(data_dic)

# Assigning the scraped links to the column 'product_url'
data['product_url'] = product_links

# Scraping data of all required features
for product in range(len(data)):
    product_url = data['product_url'].iloc[product]
    product_content = extract_content(product_url)

    # brands
    brand_data(product_content)

    # product_name
    product_name(product_content)

    # number_of_reviews
    reviews_data(product_content)

    # love_count
    love_data(product_content)

    # star_rating
    star_data(product_content)

    # price
    price_data(product_content)

    # ingredients
    ingredients_data(product_content)

    # Fragrance Family
    fragrance_family()

    # Scent Type
    scent_data()

    # Key Notes
    key_notes()

    # Fragrance Description
    fragrance_description()

    # COMPOSITION
    composition_data()

# Saving the dataframe into a csv file
data.to_csv('sephora_scraped_data.csv')
