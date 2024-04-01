"""Module that handles passenger demand computations
"""

from datetime import date

from code.worldbank import WorldBank
from code.helpers import get_city_population_geonames
from code.demand_functions import (
    _compute_base_demand,
    _get_seasonality_factor,
    _get_first_class_multiplier,
    _get_business_class_multiplier,
    _get_economy_class_multiplier,
)


class PassengerDemand:
    """Class to compute passenger demand for a given route."""

    def __init__(self, route):
        self.origin = route.hub_airport
        self.destination = route.dest_airport
        self.distance = route.get_distance()
        self.origin_wb = WorldBank(self.origin.country)
        self.destination_wb = WorldBank(self.destination.country)
        self.stats = {
            "populations": self.get_populations(),
            "gdps": self.get_gdps(),
            "plis": self.get_plis(),
            "tourism_expenditures": self.get_tourism_expenditures(),
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
        return (p_i, p_j, p_i + p_j, p_i * p_j)

    def get_gdps(self) -> tuple[float, float, float, float]:
        """Get the GDPs of the origin and destination countries

        Returns
        ----------
        tuple[float, float, float, float]
            Both GDPs, plus their sum and product
        """
        gdp_i = self.origin_wb.get_gdp()
        gdp_j = self.destination_wb.get_gdp()
        return (gdp_i, gdp_j, gdp_i + gdp_j, gdp_i * gdp_j)

    def get_plis(self) -> tuple[float, float, float, float]:
        """Get the Price Level Indices of the origin and destination countries

        Returns
        ----------
        tuple[float, float, float, float]
            Both PLIs, plus their sum and product
        """
        pli_i = self.origin_wb.get_pli()
        pli_j = self.destination_wb.get_pli()
        return (pli_i, pli_j, pli_i + pli_j, pli_i * pli_j)

    def get_tourism_expenditures(self) -> tuple[float, float, float, float]:
        """Get the amount of money that tourists in both countries spend

        Returns
        ----------
        tuple[float, float, float, float]
            Both tourism expenditures, plus their sum and product
        """
        te_i = self.origin_wb.get_tourism_expenditure()
        te_j = self.destination_wb.get_tourism_expenditure()
        return (te_i, te_j, te_i + te_j, te_i * te_j)

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
        return _compute_base_demand(self.distance, **self.stats)

    def get_seasonality_factor(self) -> float:
        """Get the seasonality factor for the route

        Returns
        ----------
        float
            The seasonality factor SF as a float value between 0.5 and 1.5.
        """
        return _get_seasonality_factor(date.today())

    def get_first_class_multiplier(self) -> float:
        """Get the first class multiplier for the route

        Returns
        ----------
        float
            The first class multiplier FCM as a float value between 0 and 0.02.
        """
        return _get_first_class_multiplier(
            self.stats["gdps"][0:1], self.stats["plis"][0:1]
        )

    def get_business_class_multiplier(self) -> float:
        """Get the business class multiplier for the route

        Returns
        ----------
        float
            The business class multiplier BCM as a float value between 0 and 0.08.
        """
        return _get_business_class_multiplier(
            self.stats["gdps"][0:1],
            self.stats["plis"][0:1],
            self.stats["tourism_expenditures"][0:1],
            self.stats["tourism_expenditures"][3],
        )

    def get_economy_class_multiplier(self) -> float:
        """Get the economy class multiplier for the route

        Returns
        ----------
        float
            The economy class multiplier ECM as a float value between 0 and 0.8.
        """
        return _get_economy_class_multiplier(
            self.stats["populations"][0:1], self.stats["populations"][3], self.distance
        )
