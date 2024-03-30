"""Main module to run the program.
"""
from pathlib import Path
from helpers import timer
from routes import Routes
from passenger_demand import PassengerDemand
from worldbank import fetch_all_indicators


root_path = Path(__file__).parent.parent

GDP_PER_CAPITA_USD = "NY.GDP.PCAP.CD"


@timer
def write_indicators(path_to_csv: Path):
    """Writes all indicators available in the World Bank API to a CSV file.

    Parameters:
        path_to_csv (Path): the path to the CSV file.
    """
    with open(path_to_csv, 'w', encoding='utf-8') as f:
        f.write("source;indicator_id;indicator_name\n")
        for indicators in fetch_all_indicators():
            for idct in indicators:
                f.write(f"{int(idct['source']['id'])};{idct['id'].lower()};{idct['name']}\n")


if __name__ == "__main__":
    # route = Routes('LSGG', 'OMDB')
    # pops = PassengerDemand(route).get_populations()
    # gdps = PassengerDemand(route).get_gdps()
    # print(pops, gdps)
    write_indicators(root_path / 'data' / 'indicators.csv')
    