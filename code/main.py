"""Main module to run the program.
"""
from code.routes import populate_routes_in_csv
from code.constants import ROOT_PATH


if __name__ == "__main__":
    populate_routes_in_csv(ROOT_PATH / 'data/routes.csv', ROOT_PATH / 'data/destinations.csv')
