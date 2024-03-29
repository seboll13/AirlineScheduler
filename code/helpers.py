"""Helper functions for the project.
"""
from functools import wraps
from pathlib import Path
from shutil import move
from time import perf_counter
from routes import Routes


@wraps
def timer(func):
    """Decorator to measure the execution time of a function.
    """
    def wrapper(*args, **kwargs):
        start = perf_counter()
        result = func(*args, **kwargs)
        end = perf_counter()
        print(f'Execution time of {func.__name__}: {end - start:.2f} seconds.')
        return result
    return wrapper


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
