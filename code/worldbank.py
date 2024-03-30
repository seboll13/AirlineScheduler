"""Module to collect data from the World Bank API.

API calls will ressemble this:
https://api.worldbank.org/v2/country/indicator/ny.gdp.pcap.cd?date=2023&format=json
"""
from requests import get
from datetime import date
from helpers import timer
from wb_helpers import generate_country_codes_dict, BASE_URL


GDP_PER_CAPITA_USD = "ny.gdp.pcap.cd"
PRICE_LEVEL_INDEX = "pa.nus.pppc.rf"
TOURISM_EXPENDITURE = "st.int.xpnd.cd"


class WorldBank:
    """Class used for wbdata collection.
    """
    def __init__(self, country):
        self.country = country
        self.country_code = generate_country_codes_dict()[country]


    def get_category(self, category) -> float:
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


    @timer
    def get_gdp(self):
        """Gets the GDP per capita of the country.
        
        Returns
        ----------
        float
            The total market value of all produced goods and services divided by the population
        """
        return self.get_category(GDP_PER_CAPITA_USD)


    @timer
    def get_pli(self):
        """Gets the Price Level Index of the country.
        
        Returns
        ----------
        float
            The ratio of the PPP conversion factor to the exchange rate
        """
        return self.get_category(PRICE_LEVEL_INDEX)


    @timer
    def get_tourism_expenditure(self):
        """Gets the Tourism Expenditure of the country.
        
        Returns
        ----------
        float
            Amount of money (in $USD) that tourists in the given country spend
        """
        return self.get_category(TOURISM_EXPENDITURE)
