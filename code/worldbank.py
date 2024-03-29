"""Module to collect data from the World Bank API.

API calls will ressemble this:
https://api.worldbank.org/v2/country/indicator/ny.gdp.pcap.cd?date=2023&format=json
"""
from requests import get


BASE_URL = "https://api.worldbank.org/v2/"
GDP_PER_CAPITA_USD = "NY.GDP.PCAP.CD"


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
