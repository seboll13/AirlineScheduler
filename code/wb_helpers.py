"""Helper functions for the World Bank Class.
"""
from logging import getLogger, basicConfig, INFO
from pathlib import Path
from requests import get

from helpers import timer

MAX_SOURCE_ID = 89
BASE_URL = "https://api.worldbank.org/v2/"


basicConfig(filename='worldbank.log', level=INFO)
logger = getLogger(__name__)


def get_data_for_url(base_url: str, source: int, page: int) -> dict:
    """Fetches data from a given URL.
    
    Parameters
    ----------
    base_url : str
        The base URL to fetch the data from
    source : int
        The source ID
    page : int
        The page number
    
    Returns
    ----------
    dict
        The data fetched from the URL. If an error occurs, an empty dictionary is returned.
    """
    response = get(f'{base_url}indicators?source={source}&page={page}&format=json', timeout=10)
    if response.status_code != 200:
        logger.info('Skipping source %s due to HTTP error %s', source, response.status_code)
        return {}
    data = response.json()
    if len(data) != 2 or 'page' not in data[0]:
        logger.info('Unexpected data structure for source %s, skipping.', source)
        return {}
    return data


def fetch_all_indicators():
    """Generator that fetches all the indicators available in the World Bank API.
        Beware, this function is quite time consuming.
        Only run this once and save the data to a file !
    """
    source = 1
    while source <= MAX_SOURCE_ID:
        page = 1
        while True:
            data = get_data_for_url(BASE_URL, source, page)
            if not data:
                break
            page_info, page_data = data
            if page_data:
                yield page_data
            if page_info['page'] >= page_info['pages']:
                break
            page += 1
        source += 1


def generate_indicator_dict():
    """Creates a dictionary of indicator names and their respective IDs.
    
    Returns
    ----------
    dict
        A dictionary of indicator (id, name) key-value pairs
    """
    return {
        idct['id']: idct['name'] for indicators in fetch_all_indicators() for idct in indicators
    }


def generate_country_codes_dict():
    """Creates a dictionary of country names and their respective codes.
    
    Returns
    ----------
    dict
        A dictionary of country names and their respective codes
    """
    url = f'{BASE_URL}country?format=json'
    response = get(url, timeout=10)
    response.raise_for_status()
    data = response.json()
    return {
        country['name']: country['id'] for country in data[1]
    }


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
