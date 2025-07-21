import re

import requests
from bs4 import BeautifulSoup

from logging_utils.logger import console
from models.animal_entry import AnimalEntry
from typing import List

UNSET_ADJECTIVE = '—'


# "User-Agent" header mimics a web browser to avoid blocks and get correct content.
HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def fetch_wikipedia_page(url: str) -> BeautifulSoup:
    """Fetch and parse the Wikipedia page."""
    console.log(f"Fetching data from {url}")
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return BeautifulSoup(response.text, 'html.parser')


def parse_animal_entries(soup: BeautifulSoup) -> List[AnimalEntry]:
    """Parse the Wikipedia page soup and return structured AnimalEntry data."""
    tables = soup.find_all('table', class_='wikitable')
    animal_entries = []

    for table_index, table in enumerate(tables):
        headers = [th.get_text(strip=True) for th in table.find_all('th')]
        try:
            animal_idx = headers.index("Animal")
            adjective_idx = headers.index("Collateral adjective")
        except ValueError:
            # Skip tables without expected headers
            continue

        for row in table.find_all('tr')[1:]:
            cells = row.find_all(['td', 'th'])
            if len(cells) <= max(animal_idx, adjective_idx):
                continue

            animal_cell = cells[animal_idx].find('a')
            adjective_cell = cells[adjective_idx].get_text(strip=True, separator=',')

            if not animal_cell or not adjective_cell:
                continue

            animal_name = animal_cell.get('title')
            animal_href = animal_cell.get('href')
            valid_adjectives = list(filter(lambda w: len(w) > 1 or w == UNSET_ADJECTIVE, adjective_cell.split(',')))
            adjectives = [clean_text(adj).replace(UNSET_ADJECTIVE, "No known adjective") for adj in valid_adjectives]

            # for animal in animal_name:
            entry = AnimalEntry(name=animal_name, href=animal_href, collateral_adjectives=adjectives)
            animal_entries.append(entry)

    console.log(f"Extracted {len(animal_entries)} animal entries.")
    return animal_entries


def clean_text(s: str):
    pattern = r'(\s*\(.*\))|(\s*\[.*\])'
    cleaned_string = re.sub(pattern, '', s)
    return cleaned_string.strip()


def get_animal_entries(url: str = "https://en.wikipedia.org/wiki/List_of_animal_names") -> List[AnimalEntry]:
    """High-level function to fetch and parse animal entries."""
    soup = fetch_wikipedia_page(url)
    return parse_animal_entries(soup)
