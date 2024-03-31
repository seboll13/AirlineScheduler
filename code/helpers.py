"""Helper functions for the project.
"""
from functools import wraps
from pathlib import Path
from time import perf_counter
from logging import basicConfig, INFO, info
from typing import Union

import numpy as np
from requests import RequestException, get


basicConfig(level=INFO)


def timer(func):
    """Decorator to measure the execution time of a function.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = perf_counter()
        result = func(*args, **kwargs)
        end = perf_counter()
        info('Execution time of %s: %.2f seconds.', func.__name__, end - start)
        return result
    return wrapper


def normalise(value: float, _min: float, _max: float) -> float:
    """Normalises a value between 0 and 1.

    Parameters
    ----------
    value : float
        The value to normalise.
    _min : float
        The minimum value of the range.
    _max : float
        The maximum value of the range.

    Returns
    ----------
    float
        The normalised value.
    """
    return (value - _min) / (_max - _min)


def get_min_and_max_distances(routes_csv: Path) -> tuple:
    """Finds the shortest and longest routes in the csv file.

    Parameters
    ----------
    routes_csv : str
        The file path of the csv file containing all the routes.

    Returns
    ----------
    tuple[float, float]
        The minimum and maximum distances.
    """
    min_distance = np.inf
    max_distance = -np.inf
    with open(routes_csv, 'r', encoding='utf-8') as infile:
        next(infile)
        for line in infile:
            line = line.strip()
            if line:
                _, _, distance = line.split(',')
                distance = float(distance)
                min_distance = min(min_distance, distance)
                max_distance = max(max_distance, distance)
    return min_distance, max_distance


def degrees_to_radians(degrees: float) -> float:
    """Converts degrees to radians.

    Parameters
    ----------
    degrees : float
        The angle in degrees.

    Returns
    ----------
    float
        The angle in radians.
    """
    return degrees * np.pi / 180


def gc_distance(airport_coords1: tuple, airport_coords2: tuple) -> float:
    """Computes the great-circle distance between two coordinates on the Earth
        provided as two (latitude, longitude) tuples in radians.
        This basically corresponds to the shortest distance between two points of a sphere.

    Parameters
    ----------
    airport_coords1 : tuple
        A tuple containing the latitude and longitude of the first airport.
    airport_coords2 : tuple
        A tuple containing the latitude and longitude of the second airport.

    Returns
    ----------
    float
        The great-circle distance between the two airports in kilometers.

    Sources
    ----------
    https://scipython.com/book2/chapter-6-numpy/problems/p62/airport-distances/
    https://community.esri.com/t5/coordinate-reference-systems-blog/distance-on-a-sphere-the-haversine-formula/ba-p/902128#:~:text=All%20of%20these%20can%20be,longitude%20of%20the%20two%20points
    """
    def haversin(alpha: float) -> float:
        """Computes the haversine function of an angle in radians.
        
        Parameters
        ----------
        alpha : float
            The angle in radians.
            
        Returns
        ----------
        float
            The haversine function of the angle.
        """
        return np.sin(alpha/2)**2
    earth_radius_km = 6378.1
    (phi1, lambda1), (phi2, lambda2) = airport_coords1, airport_coords2
    return 2 * earth_radius_km * np.arcsin(np.sqrt(
        haversin(phi2-phi1) + np.cos(phi1)*np.cos(phi2)*haversin(lambda2-lambda1)
    ))


def get_city_population_geonames(city_name: str, username: str) -> Union[int, None]:
    """
    Fetches the population of a specified city using the GeoNames API.

    Parameters
    -----------
    city_name : str
        The name of the city to search for.
    username : str
        The username to use for the GeoNames API.

    Returns
    -----------
    int
        The population of the city, or None if no data was found.
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
