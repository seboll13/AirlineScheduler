"""Main module to run the program.
"""
from pathlib import Path
from routes import Routes
from passenger_demand import PassengerDemand


root_path = Path(__file__).parent.parent

GDP_PER_CAPITA_USD = "NY.GDP.PCAP.CD"


if __name__ == "__main__":
    route = Routes('LSGG', 'OMDB')
    pops = PassengerDemand(route).get_populations()
    gdps = PassengerDemand(route).get_gdps()
    print(pops, gdps)
