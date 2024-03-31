"""Module to handle database operations.
"""
from mysql import connector


class Database:
    """Class for connecting to the database and adding data to it.

    Attributes
    ----------
    db : mysql.connector.connection.MySQLConnection
        The connection to the database.
    cursor : mysql.connector.cursor.MySQLCursor
        The cursor to the database.
    
    Methods
    ----------
    check_if_primary_key_exists(table_name: str, pk_column: str, pk_value: str) -> bool
        Checks whether or not an entry of known primary key already exists in the table.
    process_line(line, table_name, pk_name, expected_length) -> bool
        Processes a line from a csv file and inserts it into the database.
    import_csv(file_path: str, table_name: str) -> None
        Imports data from a csv file into the database.
    add_destinations(destinations_csv: str) -> None
        Adds destinations to the database from a csv file.
    add_aircrafts(aircrafts_csv: str) -> None
        Adds aircrafts to the database from a csv file.

    Examples
    ----------
    >>> db = Database()
    >>> db.add_aircrafts('data/aircrafts.csv')
    """
    def __init__(self):
        self.db = connector.connect(
            host="localhost",
            user="root",
            password="root",
            database="AirlineDB"
        )
        self.cursor = self.db.cursor()


    def check_if_primary_key_exists(self, table_name: str, pk_column: str, pk_value: str) -> bool:
        """Checks whether or not an entry of known primary key already exists in the table.
        
        Parameters
        ----------
        table_name : str
            The name of the table to check the primary key in.
        pk_column : str
            The name of the primary key column.
        pk_value : str
            The value of the primary key to check.
        
        Returns
        -------
        bool
            True if the PK exists, False otherwise.
        """
        check_query = f'SELECT EXISTS(SELECT 1 FROM {table_name} WHERE {pk_column} = %s)'
        self.cursor.execute(check_query, (pk_value,))
        return self.cursor.fetchone()[0] == 1


    def process_line(self, line, table_name, pk_name, expected_length) -> bool:
        """Processes a line from a csv file and inserts it into the database.
        
        Parameters
        ----------
        line : str
            The line from the csv file to process.
        table_name : str
            The name of the table to insert the data into.
        pk_name : str
            The name of the primary key column.
        expected_length : int
            The expected number of values in the line.
        
        Returns
        ----------
        bool
            True if data was added, False otherwise.
        """
        line = line.strip()
        values = line.split(',')
        if len(values) == expected_length:
            try:
                # account for NULL entries and convert to int if possible
                values = [
                    None if value == '' else
                    (int(value) if value.isdigit() else value)
                    for value in values
                ]
                placeholders = ','.join(['%s'] * len(values))
                query = f"INSERT INTO {table_name} VALUES ({placeholders})"
                if not self.check_if_primary_key_exists(table_name, pk_name, values[0]):
                    self.cursor.execute(query, tuple(values))
                    return True
                print(f'Skipping line {line}, due to duplicate primary key')
            except ValueError as e:
                print(f'Error inserting {line}: {e}')
        else:
            print(f'Skipping line: {line}, due to incorrect number of values')
        return False


    def import_csv(self, file_path: str, table_name: str) -> None:
        """Imports data from a csv file into the database
        
        Parameters
        ----------
        file_path : str
            The file path of the csv file.
        table_name : str
            The name of the table to insert the data into.
        """
        with open(file_path, 'r', encoding='utf-8') as file:
            header = file.readline().split(',')
            pk_name = header[0]
            expected_length = len(header)
            data_added = False
            for line in file:
                data_added = self.process_line(
                    line, table_name, pk_name, expected_length
                ) or data_added
        self.db.commit()
        if data_added:
            print(f'Data added to {table_name}.')
        else:
            print(f'Nothing to change in {table_name}.')


    def add_hubs(self, hubs_csv: str) -> None:
        """Adds hubs to the database from a csv file
        
        Parameters
        ----------
        hubs_csv : str
            The file path of the csv file containing the hubs.
        """
        self.import_csv(hubs_csv, 'hubs')


    def add_destinations(self, destinations_csv: str) -> None:
        """Adds destinations to the database from a csv file
        
        Parameters
        ----------
        destinations_csv : str
            The file path of the csv file containing the destinations.
        """
        self.import_csv(destinations_csv, 'destinations')


    def add_aircrafts(self, aircrafts_csv: str) -> None:
        """Adds aircrafts to the database from a csv file
        
        Parameters
        ----------
        aircrafts_csv : str
            The file path of the csv file containing the aircrafts.
        """
        self.import_csv(aircrafts_csv, 'aircrafts')


    def add_fleet(self, fleet_csv: str) -> None:
        """Adds fleet to the database from a csv file
        
        Parameters
        ----------
        fleet_csv : str
            The file path of the csv file containing the fleet.
        """
        self.import_csv(fleet_csv, 'fleet')
