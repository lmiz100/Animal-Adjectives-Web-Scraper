import os
import re
import requests
from bs4 import BeautifulSoup
from typing import List

from logging_utils.logger import console
from models.animal_entry import AnimalEntry
from concurrent.futures import ThreadPoolExecutor, as_completed


# Save images to /tmp
IMAGE_DIR = "/tmp"
HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def sanitize_filename(name: str) -> str:
    """Make sure filenames are valid."""
    return re.sub(r'\W+', '_', name.lower()).strip('_')


def get_image_url_from_wikipedia(animal_href: str) -> str:
    """
    Attempt to retrieve the image URL of an animal from Wikipedia
    """
    search_url = f"https://en.wikipedia.org{animal_href}"
    response = requests.get(search_url, headers=HEADERS)
    if not response.ok:
        raise Exception(f"Failed to fetch Wikipedia page for '{animal_href}'")

    soup = BeautifulSoup(response.text, 'html.parser')
    image_element = soup.find('table', class_='infobox')

    if not image_element:
        image_element = soup.find('figure')

    img = image_element.find('img') if image_element else soup.find('div', class_='thumbimage').find('img')
    if not image_element:
        raise Exception(f"No image element found for '{animal_href}'")
    if not img:
        raise Exception(f"No image found in for '{animal_href}'")

    return f"https:{img['src']}"


def download_image(animal: AnimalEntry) -> AnimalEntry:
    """Download image for a single animal and update its path."""
    filename = sanitize_filename(animal.name) + ".jpg"
    path = os.path.join(IMAGE_DIR, filename)

    if os.path.exists(path):
        console.log(f"[yellow]Skipping download for {animal.name} (already exists)[/yellow]")
        animal.image_path = path
        return animal

    try:
        img_url = get_image_url_from_wikipedia(animal.href)
        img_data = requests.get(img_url, headers=HEADERS).content

        with open(path, 'wb') as f:
            f.write(img_data)

        console.log(f"[green]Downloaded[/green] image for {animal.name}")
        animal.image_path = path

    except Exception as e:
        console.log(f"[red]Failed[/red] to download image for {animal.name}: {e}")

    return animal


def download_images_concurrently(animals: List[AnimalEntry], max_workers: int = 10) -> List[AnimalEntry]:
    """Download images in parallel and return updated animal list."""
    console.log(f"Starting concurrent download of {len(animals)} images...")

    updated_entries = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(download_image, animal): animal for animal in animals}

        for future in as_completed(futures):
            result = future.result()
            updated_entries.append(result)

    console.log("Image downloading completed.")
    return updated_entries
