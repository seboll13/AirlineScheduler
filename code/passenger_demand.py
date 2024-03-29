"""Module that handles passenger demand computations
"""
from requests import get
from requests.exceptions import RequestException
from worldbank import WorldBank


def get_city_population_geonames(city_name, username):
    """
    Fetches the population of a specified city using the GeoNames API.

    Parameters:
    city_name (str): The name of the city.
    username (str): Your GeoNames username.

    Returns:
    int: The population of the city, or None if not found.
    """
    base_url = "http://api.geonames.org/searchJSON"
    params = {
        'q': city_name,
        'maxRows': 1,
        'username': username,
        'isNameRequired': True,
        'cities': 'cities1000' # Limits search to cities with a population > 1000
    }
    try:
        response = get(base_url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        if data['totalResultsCount'] > 0:
            population = data['geonames'][0].get('population')
            return population
        print(f"No data found for {city_name}.")
        return None
    except RequestException as e:
        print(f"Failed to retrieve data from GeoNames: {e}")
        return None


class PassengerDemand:
    """Class to compute passenger demand for a given route.
    """
    def __init__(self, route):
        self.origin = route.hub_airport
        self.destination = route.dest_airport
        self.distance = route.get_distance()


    def get_populations(self) -> tuple[int, int]:
        """Get the populations of the origin and destination cities

        Returns
        ----------
        tuple[int, int]
            The sum and product of both populations    
        """
        username = "seboll13"
        p_i = get_city_population_geonames(self.origin.location, username)
        p_j = get_city_population_geonames(self.destination.location, username)
        return (p_i+p_j, p_i*p_j)


    def get_gdps(self) -> tuple[float, float]:
        """Get the GDPs of the origin and destination countries

        Returns
        ----------
        tuple[float, float]
            The sum and product of both GDPs    
        """
        gdp_i = WorldBank(self.origin.country).get_gdp()
        gdp_j = WorldBank(self.destination.country).get_gdp()
        return (gdp_i+gdp_j, gdp_i*gdp_j)
