"""Module to handle all the demand calculation logic.
    Most of its methods are either private or protected to ensure that
    they are only used within this module.
"""

from datetime import date
from numpy import exp, log, sqrt
from scipy.stats import lognorm


WEIGHT_EF: float = 0.4
WEIGHT_PF: float = 0.3
WEIGHT_TF: float = 0.2
WEIGHT_DF: float = 1 - (WEIGHT_PF + WEIGHT_EF + WEIGHT_TF)

PEAK_SEASON_MULTIPLIER: float = 1.5
STD_SEASON_MULTIPLIER: float = 1.0
OFF_PEAK_SEASON_MULTIPLIER: float = 0.5

DEMAND_SCALING_FACTOR: int = 10_000


# --------------------------------------------------------------------- #
#                       BASE DEMAND CALCULATION                         #
# --------------------------------------------------------------------- #
def __compute_population_factor(
    populations: tuple[int, int], product_of_populations: int
) -> float:
    """Compute the population factor based on the populations of the origin and
        destination cities. It is defined as the square root of the product of
        the populations, which is then scaled by the maximum population, to ensure
        that the factor is between 0 and 1.

        Intuitively, the higher the population factor, the more people there will be
        to travel between the two cities and hence, the higher the demand.

    Parameters
    ----------
    populations : tuple[int, int]
        The populations of the origin and destination cities
    product_of_populations : int
        The product of the populations of the origin and destination cities

    Returns
    ----------
    float
        The population factor PF, where 0 <= PF <= 1.
    """
    return sqrt(product_of_populations) / max(populations)


def __compute_economic_factor(
    gdps: tuple[float, float], plis: tuple[float, float]
) -> float:
    """Compute the economic factor based on the GDPs and PLIs of the origin
        and destination countries. The procedure to compute it is as follows:
        - Calculate the adjusted GDP per capita for both countries
        - Compute the Economic Similarity Ratio (ESR) as the ratio of the adjusted
            GDP per capita for the origin and destination countries
        - The economic factor is then computed as the logistic function of the ESR.

        Note that a 10^-5 factor is added to the ESR to avoid a division by zero.

    Parameters
    ----------
    gdps : tuple[float, float]
        The GDPs of the origin and destination countries
    plis : tuple[float, float]
        The PLIs of the origin and destination countries

    Returns
    ----------
    float
        The economic factor EF, where 0 <= EF <= 1.
    """
    adjusted_gdppc_origin = gdps[0] / plis[0]
    adjusted_gdppc_dest = gdps[-1] / plis[-1]
    esr = adjusted_gdppc_origin / adjusted_gdppc_dest
    return 1 / (1 + exp(-log(esr + 1e-5)))


def __compute_tourism_factor(
    tourism_expenditures: tuple[float, float], product_of_expenditures: float
) -> float:
    """Compute the tourism factor based on the tourism expenditures of the
        origin and destination countries. It is defined as the square root
        of the product of the tourism expenditures, scaled by the maximum
        tourism expenditure to ensure that the factor is between 0 and 1.

        The higher the tourism factor, the higher the attractiveness and
        connectivity between the two cities.

    Parameters
    ----------
    tourism_expenditures : tuple[float, float]
        The tourism expenditures of the origin and destination countries
    product_of_expenditures : float
        The product of the tourism expenditures of the origin and destination countries

    Returns
    ----------
    float
        The tourism factor TF, where 0 <= TF <= 1.
    """
    return sqrt(product_of_expenditures) / max(tourism_expenditures)


def __compute_distance_factor(distance: float) -> float:
    """Compute the distance factor based on the distance between the origin
        and destination cities. It is defined as the reciprocal of the
        logarithm of the distance scaled to ensure a factor between 0 and 1.

        Naturally, the closer the cities, the higher the demand.

    Parameters
    ----------
    distance : float
        The distance between the origin and destination cities

    Returns
    ----------
    float
        The distance factor DF, where 0 <= DF <= 1.
    """
    scale = 1000
    sigma = 0.5
    pdf_value = lognorm.pdf(distance, sigma, scale=scale)
    max_pdf = lognorm.pdf(scale, sigma, scale=scale)
    return min(pdf_value / max_pdf, 1.0)


def _get_seasonality_factor(curr_date: date) -> float:
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
    match curr_month:
        case 6 | 7 | 8 | 12:
            return PEAK_SEASON_MULTIPLIER
        case 1 | 2:
            return OFF_PEAK_SEASON_MULTIPLIER
        case _:
            return STD_SEASON_MULTIPLIER


def __compute_composite_score(distance, **kwargs) -> float:
    """Computes the composite score to obtain a normalised estimation of demand potential
        based on the factors computed above.

    Returns
    ----------
    float
        The composite score, where 0 <= CS <= 1.
    """
    populations = kwargs.get("populations")
    gdps = kwargs.get("gdps")
    plis = kwargs.get("plis")
    tourism_expenditures = kwargs.get("tourism_expenditures")
    return (
        WEIGHT_PF * __compute_population_factor(populations[:2], populations[3])
        + WEIGHT_EF * __compute_economic_factor(gdps[:2], plis[:2])
        + WEIGHT_TF
        * __compute_tourism_factor(tourism_expenditures[:2], tourism_expenditures[3])
        + WEIGHT_DF * __compute_distance_factor(distance)
    )


def _compute_base_demand(distance, **kwargs) -> float:
    """Computes the base demand based on the composite score and a scaling factor

    Returns
    ----------
    float
        The base demand, where 0 <= BD <= DEMAND_SCALING_FACTOR.
    """
    return __compute_composite_score(distance, **kwargs) * DEMAND_SCALING_FACTOR


# --------------------------------------------------------------------- #
#                   CLASS-SPECIFIC DEMAND MULTIPLIERS                   #
# --------------------------------------------------------------------- #
def _get_first_class_multiplier(gdps: tuple[float, float], plis: tuple[float, float]):
    """Computes the first class multiplier score based on the economic factor and
        a class specific constant factor.

        This function will return a fraction of the base demand, which depends
        heavily on the current economic factor.

    Parameters
    ----------
    gdps : tuple[float, float]
        The GDPs of the origin and destination countries
    plis : tuple[float, float]
        The PLIs of the origin and destination countries

    Returns
    ----------
    float
        The first class multiplier, where 0 <= FCM <= 0.05.
    """
    return __compute_economic_factor(gdps, plis) * 0.05


def _get_business_class_multiplier(
    gdps: tuple[float, float],
    plis: tuple[float, float],
    tourism_expenditures: tuple[float, float],
    product_of_expenditures: float,
):
    """Computes the business class multiplier score based on both the economic and
        tourism factors, each scaled by a class specific constant factor.

        This function will return a fraction of the base demand, influenced heavily
        by both economic and business tourism factors.

    Parameters
    ----------
    gdps : tuple[float, float]
        The GDPs of the origin and destination countries
    plis : tuple[float, float]
        The PLIs of the origin and destination countries
    tourism_expenditures : tuple[float, float]
        The tourism expenditures of the origin and destination countries
    product_of_expenditures : float
        The product of the tourism expenditures of the origin and destination countries

    Returns
    ----------
    float
        The business class multiplier, where 0 <= BCM <= 0.15.
    """
    return (
        __compute_economic_factor(gdps, plis) * 0.08
        + __compute_tourism_factor(tourism_expenditures, product_of_expenditures) * 0.07
    )


def _get_economy_class_multiplier(
    populations: tuple[int, int], product_of_populations: int, distance: float
):
    """Computes the economy class multiplier score based on both the population and
        the distance factors, along with a class specific constant factor.

        This function will return a large fraction of the base demand, more sensitive to
        population and distance factors.

    Parameters
    ----------
    populations : tuple[int, int]
        The populations of the origin and destination cities
    product_of_populations : int
        The product of the populations of the origin and destination cities
    distance : float
        The distance between the origin and destination cities

    Returns
    ----------
    float
        The economy class multiplier, where 0 <= ECM <= 0.8.
    """
    return (
        __compute_population_factor(populations, product_of_populations)
        + __compute_distance_factor(distance)
    ) * 0.8
