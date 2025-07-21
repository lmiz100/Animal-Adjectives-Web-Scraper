import os
from typing import List, Dict
from jinja2 import Environment, FileSystemLoader, select_autoescape

from logging_utils.logger import console
from models.animal_entry import AnimalEntry
from collections import defaultdict


TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "templates")
OUTPUT_HTML = os.path.join("output", "animals.html")


def group_by_adjective(animals: List[AnimalEntry]) -> Dict[str, List[AnimalEntry]]:
    """Group animals under each of their collateral adjectives."""
    grouped = defaultdict(list)
    for animal in animals:
        for adjective in animal.collateral_adjectives:
            grouped[adjective].append(animal)
    return dict(grouped)


def generate_html(animals: List[AnimalEntry], output_path: str=OUTPUT_HTML):
    """Render HTML using Jinja2 and save it to output/animals.html."""
    grouped = group_by_adjective(animals)

    env = Environment(
        loader=FileSystemLoader(TEMPLATE_DIR),
        autoescape=select_autoescape(['html', 'xml'])
    )
    template = env.get_template("animals_template.html")

    rendered_html = template.render(grouped_animals=grouped)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(rendered_html)

    console.log(f"[green]HTML report generated at:[/green] {output_path}")
