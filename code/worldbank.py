"""Module to collect data from the World Bank API.

API calls will ressemble this:
https://api.worldbank.org/v2/country/indicator/ny.gdp.pcap.cd?date=2023&format=json
"""
from logging import getLogger, basicConfig, INFO
from requests import get


BASE_URL = "https://api.worldbank.org/v2/"
GDP_PER_CAPITA_USD = "NY.GDP.PCAP.CD"
MAX_SOURCE_ID = 89


basicConfig(filename='worldbank.log', level=INFO)
logger = getLogger(__name__)


def country_codes_dict():
    """Creates a dictionary of country names and their respective codes.
    
    Returns
    ----------
    dict
        A dictionary of country names and their respective codes
    """
    url = f'{BASE_URL}country?format=json'
    response = get(url, timeout=10)
    response.raise_for_status()
    data = response.json()
    return {
        country['name']: country['id'] for country in data[1]
    }


def fetch_all_indicators():
    """Generator that fetches all the indicators available in the World Bank API.
        Beware, this function is quite time consuming.
        Only run this once and save the data to a file !
    """
    source = 1
    while source <= MAX_SOURCE_ID:
        page = 1
        while True:
            url = f'{BASE_URL}indicators?source={source}&page={page}&format=json'
            response = get(url, timeout=10)
            if response.status_code != 200:
                logger.info('Skipping source %s due to HTTP error %s', source, response.status_code)
                break
            data = response.json()
            if len(data) != 2 or 'page' not in data[0]:
                logger.info('Unexpected data structure for source %s, skipping.', source)
                break
            page_info, page_data = data
            if page_data:
                yield page_data
            if page_info['page'] >= page_info['pages']:
                break
            page += 1
        source += 1


class WorldBank:
    """Class used for wbdata collection.
    """
    def __init__(self, country):
        self.country = country
        self.country_code = country_codes_dict()[country]


    def get_gdp(self):
        """Gets the GDP per capita of the country.
        
        Returns
        ----------
        float
            The GDP per capita of the country
        """
        url = f'{BASE_URL}country/{self.country_code}/indicator/{GDP_PER_CAPITA_USD}?date=2022&format=json'
        response = get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data[1][0]['value']
