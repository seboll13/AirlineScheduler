"""Module to represent a route between two airports.
"""
from pathlib import Path
from shutil import move
from airport import Airport
from passenger_demand import PassengerDemand
from helpers import degrees_to_radians, gc_distance, timer


@timer
def populate_distances_in_csv(routes_csv: Path) -> None:
    """Populates the distances of each route in the csv file.
    
    Parameters
    ----------
    routes_csv : str
        The file path of the csv file containing the routes.
    """
    temp_file = routes_csv.with_suffix('.tmp')
    with open(routes_csv, 'r', encoding='utf-8') as infile, \
        open(temp_file, 'w', encoding='utf-8') as outfile:
        header = next(infile).strip()
        outfile.write(header + ',distance\n')
        for line in infile:
            line = line.strip()
            if line:
                hub, dst = line.split(',')
                route = Routes(hub.strip(), dst.strip())
                outfile.write(f'{line},{route.distance:.2f}\n')
    # replace the original file with the updated temp file
    move(temp_file, routes_csv)


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

        Returns
        ----------
        float
            The flying distance between the two airports, in kilometers.
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


    @timer
    def get_approximate_pax_demand(self):
        """Computes the approximate demand for first, business and economy class passengers
        
        Returns
        ----------
        tuple[int, int, int]
            A 3-tuple containing the demand for first, business and economy classes.
        """
        pd = PassengerDemand(self)
        fcd = bcd = ecd = pd.get_base_demand() * pd.get_seasonality_factor()
        fcd *= pd.get_first_class_multiplier()
        bcd *= pd.get_business_class_multiplier()
        ecd *= pd.get_economy_class_multiplier()
        return (int(fcd), int(bcd), int(ecd))
