"""Module to handle validity testing for passenger demand functions."""
from unittest import TestCase, main
from code.routes import Route


HUB = 'LSGG'
DESTINATIONS = ['LSZH', 'EGLL', 'EGBB', 'BIKF', 'OMDB', 'CYUL', 'KSFO']

class TestPassengerDemand(TestCase):
    """Test cases for passenger demand functions.
    """
    def test_distance_factor(self):
        """Test the distance factor calculation.
        """
        route = Route(HUB, DESTINATIONS[0])
        print(route.get_approximate_pax_demand())


if __name__ == "__main__":
    main()
