from pathlib import Path


LAT_IDX, LON_IDX = 14,15


ROOT_DIR = Path(__file__).parent.parent
GLOBAL_AIRPORT_DB_PATH = ROOT_DIR / 'data/GlobalAirportDatabase.txt'
DESTINATIONS_CSV_PATH = ROOT_DIR / 'data/destinations.csv'


def load_airports_positions() -> dict[str, tuple[float, float]]:
    """Loads the airport locations from a local text file into a dictionary.
    
    Returns
    ----------
    dict
        A dictionary containing the airport's ICAO code as the key and
        a tuple of the latitude and longitude as the value.
    
    Sources
    ----------
    The Global Airport Database can be found here:
    https://www.partow.net/miscellaneous/airportdatabase/index.html#Downloads
    """
    coordinates = {}
    with open(GLOBAL_AIRPORT_DB_PATH, 'r', encoding='utf-8') as airports:
        for airport in airports:
            line = airport.strip()
            if not line:
                continue
            details = line.split(':')
            icao_code = details[0]
            latitude = float(details[LAT_IDX])
            longitude = float(details[LON_IDX])
            coordinates[icao_code] = (latitude, longitude)
    return coordinates


def load_airport_data() -> dict[str, tuple[str, str, str, str]]:
    """Loads the airport data from a local CSV file into a tuple.
    
    Returns
    ----------
    tuple
        A tuple containing the airport's full name, location, country, and time zone.
    """
    data = {}
    with open(DESTINATIONS_CSV_PATH, 'r', encoding='utf-8') as airports:
        next(airports) # Skip the header
        for airport in airports:
            line = airport.strip()
            if not line:
                continue
            details = line.split(',')
            data[details[0]] = (details[1], details[2], details[3], details[4])
    return data


class Airport:
    """A class to represent an airport.
    """
    def __init__(self, icao_code):
        self.icao_code = icao_code
        self.full_name, self.location, self.country, self.time_zone = load_airport_data()[icao_code]
        self.latitude = self.get_latitude_and_longitude()[0]
        self.longitude = self.get_latitude_and_longitude()[1]


    def __str__(self):
        return f"Airport: {self.full_name} ({self.icao_code})"


    def get_latitude_and_longitude(self) -> tuple[float, float]:
        """Gets the latitude and longitude of the airport from a local text file of airports.

        Returns
        ----------
        tuple
            A tuple of the latitude and longitude of the airport.
        """
        airport_positions = load_airports_positions()
        if self.icao_code in airport_positions:
            return airport_positions[self.icao_code]
        return None, None
