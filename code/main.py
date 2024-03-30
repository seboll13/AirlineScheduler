"""Main module to run the program.
"""
from pathlib import Path
from routes import Routes
from passenger_demand import PassengerDemand
from wb_helpers import get_data_for_url

root_path = Path(__file__).parent.parent


if __name__ == "__main__":
    # route = Routes('LSGG', 'OMDB')
    # pops = PassengerDemand(route).get_populations()
    # gdps = PassengerDemand(route).get_gdps()
    # print(pops, gdps)
    print(get_data_for_url('https://api.worldbank.org/v2/', 1, 1))
