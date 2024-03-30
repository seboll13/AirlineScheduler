"""Module that handles passenger demand computations
"""
from datetime import date
from requests import get
from requests.exceptions import RequestException
from numpy import exp, log, sqrt
from constants import ROOT_PATH
from helpers import get_min_and_max_distances, normalise
from worldbank import WorldBank


DEMAND_SCALING_FACTOR = 10_000


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
        self.origin_wb = WorldBank(self.origin.country)
        self.destination_wb = WorldBank(self.destination.country)
        self.stats = {
            'populations': self.get_populations(),
            'gdps': self.get_gdps(),
            'plis': self.get_plis(),
            'tourism_expenditures': self.get_tourism_expenditures()
        }


    # --------------------------------------------------------------------- #
    #                      DATA COLLECTION METHODS                          #
    # --------------------------------------------------------------------- #
    def get_populations(self) -> tuple[int, int, int, int]:
        """Get the populations of the origin and destination cities

        Returns
        ----------
        tuple[int, int, int, int]
            Both populations, plus their sum and product
        """
        username = "seboll13"
        p_i = get_city_population_geonames(self.origin.location, username)
        p_j = get_city_population_geonames(self.destination.location, username)
        return (p_i, p_j, p_i+p_j, p_i*p_j)


    def get_gdps(self) -> tuple[float, float, float, float]:
        """Get the GDPs of the origin and destination countries

        Returns
        ----------
        tuple[float, float, float, float]
            Both GDPs, plus their sum and product
        """
        gdp_i = self.origin_wb.get_gdp()
        gdp_j = self.destination_wb.get_gdp()
        return (gdp_i, gdp_j, gdp_i+gdp_j, gdp_i*gdp_j)


    def get_plis(self) -> tuple[float, float, float, float]:
        """Get the Price Level Indices of the origin and destination countries

        Returns
        ----------
        tuple[float, float, float, float]
            Both PLIs, plus their sum and product  
        """
        pli_i = self.origin_wb.get_pli()
        pli_j =self.destination_wb.get_pli()
        return (pli_i, pli_j, pli_i+pli_j, pli_i*pli_j)


    def get_tourism_expenditures(self) -> tuple[float, float, float, float]:
        """Get the amount of money that tourists in both countries spend

        Returns
        ----------
        tuple[float, float, float, float]
            Both tourism expenditures, plus their sum and product
        """
        te_i = self.origin_wb.get_tourism_expenditure()
        te_j = self.destination_wb.get_tourism_expenditure()
        return (te_i, te_j, te_i+te_j, te_i*te_j)


    # --------------------------------------------------------------------- #
    #                        PUBLIC ACCESS METHODS                          #
    # --------------------------------------------------------------------- #
    def get_base_demand(self) -> float:
        """Get the base demand for the route

        Returns
        ----------
        float
            The base demand BD as a float value between 0 and 1.
        """
        return self.__compute_base_demand()


    def get_seasonality_factor(self) -> float:
        """Get the seasonality factor for the route

        Returns
        ----------
        float
            The seasonality factor SF as a float value between 0.5 and 1.5.
        """
        return self.__get_seasonality_factor(date.today())


    def get_first_class_multiplier(self) -> float:
        """Get the first class multiplier for the route

        Returns
        ----------
        float
            The first class multiplier FCM as a float value between 0 and 0.02.
        """
        return self.__get_first_class_multiplier()


    def get_business_class_multiplier(self) -> float:
        """Get the business class multiplier for the route

        Returns
        ----------
        float
            The business class multiplier BCM as a float value between 0 and 0.08.
        """
        return self.__get_business_class_multiplier()


    def get_economy_class_multiplier(self) -> float:
        """Get the economy class multiplier for the route

        Returns
        ----------
        float
            The economy class multiplier ECM as a float value between 0 and 0.8.
        """
        return self.__get_economy_class_multiplier()


    # --------------------------------------------------------------------- #
    #                       BASE DEMAND CALCULATION                         #
    # --------------------------------------------------------------------- #
    def __compute_population_factor(self) -> float:
        """Compute the population factor based on the populations of the origin and
            destination cities. It is defined as the square root of the product of
            the populations, which is then scaled by the maximum population, to ensure
            that the factor is between 0 and 1.

            Intuitively, the higher the population factor, the more people there will be
            to travel between the two cities and hence, the higher the demand.
        
        Returns
        ----------
        float
            The population factor PF, where 0 <= PF <= 1.
        """
        max_pop = max(self.stats['populations'][0], self.stats['populations'][1])
        return sqrt(self.stats['populations'][3]) / max_pop


    def __compute_economic_factor(self) -> float:
        """Compute the economic factor based on the GDPs and PLIs of the origin
            and destination countries. The procedure to compute it is as follows:
            - Calculate the adjusted GDP per capita for both countries
            - Compute the Economic Similarity Ratio (ESR) as the ratio of the adjusted
                GDP per capita for the origin and destination countries
            - The economic factor is then computed as the logistic function of the ESR.

            Note that a 10^-5 factor is added to the ESR to avoid a division by zero.

        Returns
        ----------
        float
            The economic factor EF, where 0 <= EF <= 1.
        """
        adjusted_gdppc_origin = self.stats['gdps'][0] / self.stats['plis'][0]
        adjusted_gdppc_dest = self.stats['gdps'][1] / self.stats['plis'][1]
        esr = adjusted_gdppc_origin / adjusted_gdppc_dest
        return 1 / (1 + exp(-log(esr + 1e-5)))


    def __compute_tourism_factor(self) -> float:
        """Compute the tourism factor based on the tourism expenditures of the
            origin and destination countries. It is defined as the square root
            of the product of the tourism expenditures, scaled by the maximum
            tourism expenditure to ensure that the factor is between 0 and 1.

            The higher the tourism factor, the higher the attractiveness and 
            connectivity between the two cities.

        Returns
        ----------
        float
            The tourism factor TF, where 0 <= TF <= 1.
        """
        max_te = max(
            self.stats['tourism_expenditures'][0], self.stats['tourism_expenditures'][1]
        )
        return sqrt(self.stats['tourism_expenditures'][3]) / max_te


    def __compute_distance_factor(self) -> float:
        """Compute the distance factor based on the distance between the origin
            and destination cities. It is defined as the reciprocal of the
            logarithm of the distance scaled to ensure a factor between 0 and 1.

            Naturally, the closer the cities, the higher the demand.

        Returns
        ----------
        float
            The distance factor DF, where 0 <= DF <= 1.
        """
        min_dist, max_dist = get_min_and_max_distances(ROOT_PATH / 'data/routes.csv')
        return normalise(1 / log(self.distance), 1 / log(max_dist), 1 / log(min_dist))


    def __get_seasonality_factor(self, curr_date: date) -> float:
        """Simple function to get a seasonality factor that varies
            with respect to the time of year.

            Peak times are considered to be the summer holidays and Christmas.
            The rest are standard times, except January and February which
            are considered off-peak.

        Parameters
        ----------
        curr_date : date
            The date at the time the function is called
        
        Returns
        ----------
        float
            The seasonality factor SF, where 0.5 <= SF <= 1.5.
        """
        curr_month = curr_date.month
        if 6 <= curr_month <= 8 or curr_month == 12:
            return 1.5
        if curr_month in [1,2]:
            return 0.5
        return 1.0


    def __compute_composite_score(self) -> float:
        """Computes the composite score to obtain a normalised estimation of demand potential
            based on the factors computed above.
        
        Returns
        ----------
        float
            The composite score, where 0 <= CS <= 1.
        """
        weight_pf: float = 0.3
        weight_ef: float = 0.3
        weight_tf: float = 0.2
        weight_df: float = 0.2
        return (
            weight_pf * self.__compute_population_factor() +
            weight_ef * self.__compute_economic_factor() +
            weight_tf * self.__compute_tourism_factor() +
            weight_df * self.__compute_distance_factor()
        )


    def __compute_base_demand(self) -> float:
        """Computes the base demand based on the composite score and a scaling factor
        
        Returns
        ----------
        float
            The base demand, where 0 <= BD <= DEMAND_SCALING_FACTOR.
        """
        return self.__compute_composite_score() * DEMAND_SCALING_FACTOR


    # --------------------------------------------------------------------- #
    #                   CLASS-SPECIFIC DEMAND MULTIPLIERS                   #
    # --------------------------------------------------------------------- #
    def __get_first_class_multiplier(self):
        """Computes the first class multiplier score based on the economic factor and 
            a class specific constant factor.
            
            This function will return a fraction of the base demand, which depends
            heavily on the current economic factor.
        
        Returns
        ----------
        float
            The first class multiplier, where 0 <= FCM <= 0.02.
        """
        return self.__compute_economic_factor() * 0.02


    def __get_business_class_multiplier(self):
        """Computes the business class multiplier score based on both the economic and
            tourism factors, each scaled by a class specific constant factor.
            
            This function will return a fraction of the base demand, influenced heavily
            by both economic and business tourism factors.
        
        Returns
        ----------
        float
            The business class multiplier, where 0 <= BCM <= 0.08.
        """
        return self.__compute_economic_factor() * 0.05 + self.__compute_tourism_factor() * 0.03


    def __get_economy_class_multiplier(self):
        """Computes the economy class multiplier score based on both the population and
            the distance factors, along with a class specific constant factor.
            
            This function will return a large fraction of the base demand, more sensitive to
            population and distance factors.
        
        Returns
        ----------
        float
            The economy class multiplier, where 0 <= ECM <= 0.8.
        """
        return (self.__compute_population_factor() + self.__compute_distance_factor()) * 0.8
