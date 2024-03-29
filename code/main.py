"""Main module to run the program.
"""
from pathlib import Path
from routes import Routes
from passenger_demand import PassengerDemand


root_path = Path(__file__).parent.parent


if __name__ == "__main__":
    route = Routes('LSGG', 'LFPO')
    pd = PassengerDemand(route)
    print(pd.get_populations())
