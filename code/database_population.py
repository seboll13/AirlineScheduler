from mysql import connector


class Database:
    """Class for connecting to the database and adding data to it.
    """
    def __init__(self):
        self.db = connector.connect(
            host="localhost",
            user="root",
            password="root",
            database="AirlineDB"
        )
        self.cursor = self.db.cursor()


def add_destinations(self, destinations_csv: str):
    """Adds destinations to the database from a csv file
    
    Parameters
    ----------
    destinations_csv : str
        The file path of the csv file containing the destinations.
    """
    with open(destinations_csv, 'r', encoding='utf-8') as file:
        next(file) # skips the header
        for line in file:
            line = line.strip()
            values = line.split(',')
            if len(values) == 5:
                try:
                    values[4] = int(values[4])
                    self.cursor.execute(
                        "INSERT INTO destinations (destination_icao,name,location,country,time_zone) VALUES (%s,%s,%s,%s,%s)", 
                        (values[0],values[1],values[2],values[3],values[4])
                    )
                except ValueError:
                    print(f'Error inserting {line}')
            else:
                print(f'Skipping line: {line}, due to incorrect number of values')
        self.db.commit()
        print('Destinations added.')
