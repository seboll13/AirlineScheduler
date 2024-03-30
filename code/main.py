"""Main module to run the program.
"""
from routes import Routes


DEP_ICAO = 'LSGG'
ARR_ICAO = 'OMDB'


if __name__ == "__main__":
    route_1 = Routes(DEP_ICAO, ARR_ICAO)
    print(f'Demand for {DEP_ICAO}-{ARR_ICAO}: {route_1.get_approximate_pax_demand()}')

    route_2 = Routes(ARR_ICAO, DEP_ICAO)
    print(f'Demand for {ARR_ICAO}-{DEP_ICAO}: {route_2.get_approximate_pax_demand()}')
