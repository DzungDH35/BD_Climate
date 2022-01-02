from bs4 import BeautifulSoup
import os
import requests
import time
from requests.api import get
from requests.sessions import Request
import urllib3

# disable SSL Cert warning when running requests.get()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

CSV_DATA_DIR = 'data/csv'

BASE_URL = 'https://en.tutiempo.net'
BASE_CLIMATE_URL = BASE_URL + '/climate'

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

def get_available_years(CITY_LINK):
    years = []
    raw_html = requests.get(BASE_URL + CITY_LINK, verify = False).text.encode('utf=8') # warning: no cert configuration
    html_soup = BeautifulSoup(raw_html, 'html.parser')
    html_data_table_type_1 = html_soup.find('div', class_='mlistados')
    html_data_table_type_2 = html_soup.find('table', class_='medias')

    a_tags = []
    if (html_data_table_type_1 is not None):
        a_tags = html_data_table_type_1.find_all('a')
    elif (html_data_table_type_2 is not None):
        a_tags = html_data_table_type_2.find_all('a')
    
    if len(a_tags) > 0:
        for a_tag in a_tags:
            year = a_tag['href'].split('/')[2]
            years.append(int(year))
    
    return years

def get_available_months(YEAR, CITY_LINK):
    months = []
    city_id = CITY_LINK.split('/')[2]
    raw_html = requests.get('{}/{}/{}'.format(BASE_CLIMATE_URL, YEAR, city_id), verify = False).text.encode('utf=8') # warning: no cert configuration
    html_soup = BeautifulSoup(raw_html, 'html.parser')
    html_data_table = html_soup.find('div', class_='mlistados')
    a_tags = html_data_table.find_all('a')

    for a_tag in a_tags:
        month = a_tag['href'].split('/')[2].split('-')[0].lstrip('0')
        months.append(int(month))
    
    return months

def crawl_climate_data(city_link, STORE_PATH):
    climate_url = ''

    available_years = get_available_years(city_link)
    available_months = ''
    climate_url = ''
    raw_html = ''
    html_soup = ''
    html_data_table= ''
    html_rows = ''

    for year in available_years:
        available_months = get_available_months(year, city_link)

        for month in available_months:
            climate_url = construct_climate_url(month, year, city_link)
            print(climate_url)

            raw_html = ''
            while raw_html == '':
                try:
                    raw_html = requests.get(climate_url, verify=False, timeout=5).text.encode('utf=8') # warning: no cert configuration
                except requests.exceptions.Timeout:
                    continue

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
    
    temp1 = ''
    temp2 = ''
    for continent_k, continent_v in continents.items():
        store_path = CSV_DATA_DIR + '/' + continent_k
        temp1 = store_path
        countries = get_countries(continent_v['href'])

        print(continent_k, end=" ")
        for country_k, country_v in countries.items():
            if (country_k == 'Albania'):
                continue
            store_path = temp1 + '/' + country_k
            temp2 = store_path
            cities = get_cities(country_v['href'])
            print(country_k, end=" ")
            for city_k, city_v in cities.items():
                if os.path.exists('data/csv/{}/{}/{}'.format(continent_k, country_k, city_k)):
                    continue
                store_path = temp2 + '/' + city_k

                if not os.path.exists(store_path):
                    os.makedirs(store_path)
                
                print(city_k, end=" ")
                crawl_climate_data(city_v['href'], store_path)

    stop_time = time.time()
    print("Time taken: {} seconds.".format(stop_time - start_time))