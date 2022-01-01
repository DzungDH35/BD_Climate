from bs4 import BeautifulSoup
import os
import requests
import time
from requests.api import get
import urllib3

# disable SSL Cert warning when running requests.get()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

CSV_DATA_DIR = 'data/csv'

BASE_URL = 'https://en.tutiempo.net'
BASE_CLIMATE_URL = BASE_URL + '/climate'

START_YEAR = 1900
END_YEAR = 2021
START_MONTH = 1
END_MONTH = 12

HTML_CLASSES_TO_NUMBERS = {
    'ntio': '-', 'ntjj': '-', 'ntzz': '-', 'ntkf': '-',
    'ntyc': '.', 'ntkk': '.', 'ntvr': '.', 'ntux': '.',
    'ntde': '0', 'ntfg': '0', 'ntbc': '0', 'ntab': '0',
    'ntlm': '1', 'ntno': '1', 'ntjk': '1', 'nthi': '1',
    'nttu': '2', 'ntvw': '2', 'ntrs': '2', 'ntpq': '2',
    'ntcd': '3', 'ntef': '3', 'ntza': '3', 'ntxy': '3',
    'ntbb': '4', 'ntee': '4', 'ntaa': '4', 'ntgg': '4',
    'ntzb': '5', 'ntgo': '5', 'ntbz': '5', 'ntaz': '5',
    'nthj': '6', 'ntdr': '6', 'ntgy': '6', 'ntyy': '6',
    'ntfs': '7', 'ntpo': '7', 'ntox': '7', 'ntxo': '7',
    'ntas': '8', 'nthy': '8', 'ntqr': '8', 'ntre': '8',
    'nttn': '9', 'ntjg': '9', 'ntnt': '9', 'ntll': '9'
}

def init():
    if not os.path.exists(CSV_DATA_DIR):
        os.makedirs(CSV_DATA_DIR)

def get_continents():
    continents = {}
    raw_html = requests.get(BASE_CLIMATE_URL, verify = False).text.encode('utf=8') # warning with no cert configuration
    html_soup = BeautifulSoup(raw_html, 'html.parser')
    table = html_soup.find(class_='mlistados mt10')
    a_tags = table.find_all('a')

    for a in a_tags:
        continents[a.string] = {}
        continents[a.string]['href'] = a['href']

    return continents

def get_countries(continent_link):
    countries = {}
    raw_html = requests.get('{}{}'.format(BASE_URL, continent_link), verify = False).text.encode('utf=8') # warning with no cert configuration
    html_soup = BeautifulSoup(raw_html, 'html.parser')
    table = html_soup.find(class_='mlistados mt10')
    a_tags = table.find_all('a')

    for a in a_tags:
        countries[a.string] = {}
        countries[a.string]['href'] = a['href']
    
    return countries

def get_cities(country_link):
    cities = {}
    raw_html = requests.get('{}{}'.format(BASE_URL, country_link), verify = False).text.encode('utf=8') # warning with no cert configuration
    html_soup = BeautifulSoup(raw_html, 'html.parser')
    tables = html_soup.find_all(class_='mlistados mt10')

    for table in tables:
        a_tags = table.find_all('a')
        for a in a_tags:
            if a.string in cities:
                a.string += '_plus'
            cities[a.string] = {}
            cities[a.string]['href'] = a['href']
    
    return cities

def construct_climate_url(month, year, city_link):
    climate_url = ''
    city_id = city_link.split('/')[2]

    if month < 10:
        climate_url = '{}/0{}-{}/{}'.format(BASE_CLIMATE_URL, month, year, city_id)
    else:
        climate_url = '{}/{}-{}/{}'.format(BASE_CLIMATE_URL, month, year, city_id)

    return climate_url

def crawl_climate_data(city_link, STORE_PATH):
    climate_url = ''

    # adjust later
    for year in range(1900, 1901):
        for month in range(1, 2):
            climate_url = construct_climate_url(month, year, city_link)
            raw_html = requests.get(climate_url, verify = False).text.encode('utf=8') # warning: no cert configuration
            html_soup = BeautifulSoup(raw_html, 'html.parser')
            html_data_table = html_soup.find('table', class_='medias mensuales numspan')

            html_rows = ''
            if (html_data_table is not None):
                html_rows = html_data_table.find_all('tr')

                # delete the last two redundant <tr> rows
                html_rows.pop()
                html_rows.pop()

                # replace all special <span> tags with corresponding numbers
                for class_key in HTML_CLASSES_TO_NUMBERS.keys():
                    for span in html_data_table.find_all('span', class_=class_key):
                        span.replace_with(HTML_CLASSES_TO_NUMBERS[class_key])

                # reformat content of data <td> colummns
                for td in html_data_table.find_all('td'):
                    if (td.string == '\xa0' or td.string == 'o' or td.string == '-'):
                        td.string = ''
                    else:
                        td.string = td.get_text()
                
                if not os.path.exists('{}/{}'.format(STORE_PATH, year)):
                    os.makedirs('{}/{}'.format(STORE_PATH, year))

                with open("{}/{}/{}.csv".format(STORE_PATH, year, month), "w", encoding='utf-8') as f:
                    for html_row in html_rows:
                        f.write(html_row.get_text(','))
                        f.write('\n')

if __name__ == '__main__':    
    init()
    store_path = ''
    continents = get_continents()
    countries = []

    start_time = time.time()

    for continent_k, continent_v in continents.items():
        store_path = CSV_DATA_DIR + '/' + continent_k
        countries = get_countries(continent_v['href'])

        for country_k, country_v in countries.items():
            store_path += '/' + country_k
            cities = get_cities(country_v['href'])

            for city_k, city_v in cities.items():
                store_path += '/' + city_k

                if not os.path.exists(store_path):
                    os.makedirs(store_path)
                
                crawl_climate_data(city_v['href'], store_path)

    stop_time = time.time()
    print("Time taken: {} seconds.".format(stop_time - start_time))