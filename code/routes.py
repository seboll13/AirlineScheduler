import numpy as np
from airport import Airport


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
    d = 2 * earth_radius_km * np.arcsin(np.sqrt(
        haversin(phi2-phi1) + np.cos(phi1)*np.cos(phi2)*haversin(lambda2-lambda1)
    ))
    return d


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


class Routes:
    """A class to represent a route between two airports.
    """
    def __init__(self, hub_icao, dest_icao):
        self.hub_airport = Airport(hub_icao)
        self.dest_airport = Airport(dest_icao)
        if self.dest_airport.latitude is None or self.dest_airport.longitude is None:
            raise ValueError(f'No such airport with ICAO code {dest_icao}')
        self.distance = self.get_distance()


    def get_distance(self):
        """Gets the flying distance of the route
        """
        hub_coords = (
            degrees_to_radians(self.hub_airport.latitude),
            degrees_to_radians(self.hub_airport.longitude)
        )
        dest_coords = (
            degrees_to_radians(self.dest_airport.latitude),
            degrees_to_radians(self.dest_airport.longitude)
        )
        return gc_distance(hub_coords, dest_coords)
