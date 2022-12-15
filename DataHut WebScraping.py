# Importing libraries
import time
import random
import requests
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


# Continuously clicking the button to show more products till everything is loaded
def pagination():
    total_num_of_products = driver.find_element(By.XPATH, "//div[@class='css-unii66']/p").text
    total_num_of_products = total_num_of_products.split(' ')
    total_num_of_products = int(total_num_of_products[2])
    click_count = 0
    while click_count < (total_num_of_products / 60) + 1:  # Since number of products loaded per click is 60
        try:
            driver.find_element(By.XPATH, "//div[@class='css-unii66']/button").click()
            delay()
            click_count += 1
        except:
            click_count += 1
            pass


# Scrolling down the page in order to overcome Lazy Loading
def lazy_loading():
    delay()
    element = driver.find_element(By.TAG_NAME, 'body')
    while True:
        element.send_keys(Keys.PAGE_DOWN)
        delay()


def fetch_product_links(ap):
    for one_product in ap.find_all('div', {'class': 'css-foh208'}):
        #     for one_product_link in one_product.find_all('a', {'class':'css-klx76'}):
        for one_product_link in one_product.find_all('a'):
            if one_product_link['href'].startswith('https:'):
                product_links.append(one_product_link['href'])
            else:
                product_links.append('https://www.sephora.com' + one_product_link['href'])


def fetch_lazy_loading_product_links(ap):
    for one_product in ap.find_all('div', {'class': 'css-1qe8tjm'}):
        for one_product_link in one_product.find_all('a', {'class': 'css-klx76'}):
            if one_product_link['href'].startswith('https:'):
                product_links.append(one_product_link['href'])
            else:
                product_links.append('https://www.sephora.com' + one_product_link['href'])


def extract_content(url):
    page_content = requests.get(url, headers=header)
    product_soup = BeautifulSoup(page_content.content, 'html.parser')
    return product_soup


def brand_data(soup):
    brand = soup.find('a', attrs={"data-at": "brand_name"}).text
    data['brand'].iloc[each_product] = brand


def product_name(soup):
    product = soup.find('span', attrs={"data-at": "product_name"}).text
    data['product_name'].iloc[each_product] = product


def reviews_data(soup):
    reviews = soup.find('span', attrs={"data-at": "number_of_reviews"}).text
    data['number_of_reviews'].iloc[each_product] = reviews


def love_data(soup):
    love = soup.find('span', attrs={"class": "css-jk94q9"}).text
    data['love_count'].iloc[each_product] = love


def star_data(soup):
    star = soup.find('span', attrs={"class": "css-1tbjoxk"})['aria-label']
    data['star_rating'].iloc[each_product] = star


def price_data(soup):
    price = soup.find('b', attrs={"class": "css-0"}).text
    data['price'].iloc[each_product] = price


def ingredients_data(soup):
    for ingredient in soup.find('div', attrs={"class": "css-1ue8dmw eanm77i0"}):
        if len(ingredient.contents) == 1:
            try:
                data['Ingredients'].iloc[each_product] = ingredient.contents[0].text
            except:
                data['Ingredients'].iloc[each_product] = ingredient.contents[0]
        else:
            data['Ingredients'].iloc[each_product] = ingredient.contents[1]


def fragrance_data(kv):
    if kv[0] == 'Fragrance Family':
        data['Fragrance Family'].iloc[each_product] = kv[1]


def scent_data(kv):
    if kv[0] == 'Scent Type':
        data['Scent Type'].iloc[each_product] = kv[1]


def keynotes(kv):
    if kv[0] == 'Key Notes':
        data['Key Notes'].iloc[each_product] = kv[1]


def fragrance(kv):
    if kv[0] == 'Fragrance Description':
        data['Fragrance Description'].iloc[each_product] = kv[1]


def composition_data(kv):
    if kv[0].lower() == 'composition':
        data['COMPOSITION'].iloc[each_product] = kv[1]


# Sephora website link
site_url = 'https://www.sephora.com/shop/fragrances-for-women'
header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/81.0.4044.138 Safari/537.36"}
driver.get(site_url)

# Converting the content of the page to BeautifulSoup object
content = driver.page_source
homepage_soup = BeautifulSoup(content, 'html5lib')

# Fetching the product links of all items
product_links = []
all_products = homepage_soup.find_all('div', attrs={"class": "css-1322gsb"})[0]
fetch_product_links(all_products)
fetch_lazy_loading_product_links(all_products)  # Fetching the product links- Continuation (Lazy loaded items)

# Reading the given sample data f=pd.read_csv('Downloads\\Sephora Sample data - Sheet1.csv')
sample_df = pd.read_csv('Downloads\\Sephora Sample data - Sheet1.csv')

# Creating a dictionary of the required columns
data_dic = {'product_url': [], 'brand': [], 'product_name': [],
            'number_of_reviews': [], 'love_count': [], 'star_rating': [], 'price': [], 'Fragrance Family': [],
            'Scent Type': [], 'Key Notes': [], 'Fragrance Description': [], 'COMPOSITION': [], 'Ingredients': []}

# Creating a dataframe with those columns
data = pd.DataFrame(data_dic)

# Assigning the scraped links to the column 'product_url'
data['product_url'] = product_links

# Scraping data like 'brand_name','product_name','number_of_reviews','love_count','star_rating' and 'price'
for each_product in range(len(data)):
    product_url = data['product_url'].iloc[each_product]
    product_content = extract_content(product_url)

    try:
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


    except:
        pass

# Scraping data of ingredients
for each_product in range(len(data)):
    product_url = data['product_url'].iloc[each_product]
    product_content = extract_content(product_url)

    try:
        ingredients_data(product_content)

    except:
        pass

# Scraping the remaining data like 'Fragrance Family','Scent Type','Key Notes','Fragrance Description' and 'Composition'
for each_product in range(len(data)):
    driver.get(data['product_url'].iloc[each_product])

    try:
        section = driver.find_element(By.XPATH, "//div[@class='css-32uy52 eanm77i0']").text
        split_section = section.split('\n')
        for feature in split_section:
            keys_values = feature.split(':')

            # Fragrance Family
            fragrance_data(keys_values)

            # Scent Type
            scent_data(keys_values)

            # Key Notes
            keynotes(keys_values)

            # Fragrance Description
            fragrance(keys_values)

            # COMPOSITION
            composition_data(keys_values)


    except:
        pass
