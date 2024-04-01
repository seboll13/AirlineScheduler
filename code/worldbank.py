"""Module to collect data from the World Bank API.

API calls will ressemble this:
https://api.worldbank.org/v2/country/indicator/ny.gdp.pcap.cd?date=2023&format=json
"""
import shelve
from datetime import date

from code.helpers import timer
from code.wb_helpers import fetch_country_codes, BASE_URL

from requests import get

GDP_PER_CAPITA_USD = "ny.gdp.pcap.cd"
PRICE_LEVEL_INDEX = "pa.nus.pppc.rf"
TOURISM_EXPENDITURE = "st.int.xpnd.cd"

COUNTRY_CODES = dict(fetch_country_codes())

KNOWN_EXCEPTIONS = {
    'Czech Republic': 'Czechia',
    'Turkey': 'Turkiye',
    'Slovakia': 'Slovak Republic',
    'South Korea': 'Korea, Rep.',
}


class WorldBank:
    """Class used for wbdata collection.
    """
    def __init__(self, country):
        if country in COUNTRY_CODES:
            self.country = country
            self.country_code = COUNTRY_CODES[country]
        else:
            keys = list(COUNTRY_CODES.keys())
            # check if the country appears as substring of one of the keys
            for key in keys:
                if country in key:
                    self.country = key
                    self.country_code = COUNTRY_CODES[key]
                    break
            else:
                if country not in KNOWN_EXCEPTIONS:
                    raise ValueError(f'Country {country} not found in the World Bank API')
                wb_name = KNOWN_EXCEPTIONS[country]
                self.country = wb_name
                self.country_code = COUNTRY_CODES[wb_name]


    def get_category(self, category: str) -> float:
        """Gets the data for a given category.
        
        Parameters
        ----------
        category : str
            The category to get the data for
        
        Returns
        ----------
        float
            The data for the given category; -1.0 if no data is found
        """
        curr_year = date.today().year
        while True:
            url = f'{BASE_URL}country/{self.country_code}/indicator/{category}?date={curr_year}&format=json'
            response = get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            if data[1]:
                value = data[1][0].get('value')
                if value is not None:
                    return float(value)
            curr_year -= 1
            if curr_year < 1960:
                return -1.0


    def get_category_with_cache(self, category: str) -> float:
        """Gets a specific cateogry with caching.
        
        Parameters
        ----------
        category : str
            The category to get the data for
        
        Returns
        ----------
        float
            The data for the given category; -1.0 if no data is found
        """
        with shelve.open(f'caches/{category}_cache') as db:
            if self.country_code in db:
                return db[self.country_code]
            value = self.get_category(category)
            db[self.country_code] = value
            return value


    @timer
    def get_gdp(self):
        """Gets the GDP per capita of the country.
        
        Returns
        ----------
        float
            The total market value of all produced goods and services divided by the population
        """
        return self.get_category_with_cache(GDP_PER_CAPITA_USD)


    @timer
    def get_pli(self):
        """Gets the Price Level Index of the country.
        
        Returns
        ----------
        float
            The ratio of the PPP conversion factor to the exchange rate
        """
        return self.get_category_with_cache(PRICE_LEVEL_INDEX)


    @timer
    def get_tourism_expenditure(self):
        """Gets the Tourism Expenditure of the country.
        
        Returns
        ----------
        float
            Amount of money (in $USD) that tourists in the given country spend
        """
        return self.get_category_with_cache(TOURISM_EXPENDITURE)
