"""Module to handle validity testing for passenger demand functions."""
from datetime import date
from unittest import TestCase, main

from code.demand_functions import (
    _compute_base_demand, _get_business_class_multiplier, _get_economy_class_multiplier, _get_first_class_multiplier, _get_seasonality_factor,
    PEAK_SEASON_MULTIPLIER, OFF_PEAK_SEASON_MULTIPLIER, STD_SEASON_MULTIPLIER
)


HUB = 'LSGG'
DESTINATIONS = ['LSZH', 'EGLL', 'EGBB', 'BIKF', 'OMDB', 'CYUL', 'KSFO']


class TestPassengerDemand(TestCase):
    """Test cases for passenger demand functions.
    """
    stats = {
        'populations': (1_000, 2_000, 3_000, 2_000_000),
        'gdps': (10, 30, 50, 300),
        'plis': (1.1, 1.2, 2.3, 1.32),
        'tourism_expenditures': (20, 40, 60, 800)
    }


    def test_base_demand_increases_for_shorter_distances(self):
        """Checks that base demand increases for distances under 1000km.
        """
        base_demand = _compute_base_demand(100, **self.stats)
        self.assertLess(base_demand, _compute_base_demand(200, **self.stats))


    def test_base_demand_decreases_for_longer_distances(self):
        """Checks that base demand decreases for distances over 1000km.
        """
        base_demand = _compute_base_demand(1000, **self.stats)
        self.assertGreater(base_demand, _compute_base_demand(2000, **self.stats))


    def test_class_multipliers_are_within_bounds(self):
        """Checks that class multipliers are within the expected bounds.
        """
        fcm = _get_first_class_multiplier(
            self.stats['gdps'][:2], self.stats['plis'][:2]
        )
        self.assertLessEqual(fcm, 0.02)
        bcm = _get_business_class_multiplier(
            self.stats['gdps'][:2], self.stats['plis'][:2],
            self.stats['tourism_expenditures'][:2],
            self.stats['tourism_expenditures'][3]
        )
        self.assertLessEqual(bcm, 0.08)
        ecm = _get_economy_class_multiplier(
            self.stats['populations'][:2], self.stats['populations'][3], 100
        )
        self.assertLessEqual(ecm, 0.8)


    def test_correctness_of_seasonality_factor(self):
        """Checks that the seasonality factor changes correctly with the month.
        """
        self.assertEqual(
            _get_seasonality_factor(date(2023,1,1)), OFF_PEAK_SEASON_MULTIPLIER
        )
        self.assertEqual(
            _get_seasonality_factor(date(2023,6,1)), PEAK_SEASON_MULTIPLIER
        )
        self.assertEqual(
            _get_seasonality_factor(date(2023,9,1)), STD_SEASON_MULTIPLIER
        )


if __name__ == "__main__":
    main()
