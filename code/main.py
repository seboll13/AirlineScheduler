"""Main module to run the program.
"""
from pathlib import Path
from shutil import move
from helpers import timer
from routes import Routes


root_path = Path(__file__).parent.parent


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
    move(temp_file, routes_csv) # replaces the original file with the updated temp file


if __name__ == "__main__":
    populate_distances_in_csv(root_path / 'data/routes.csv')
