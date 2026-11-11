import csv
import random
from functools import lru_cache
from pathlib import Path

from items.item_factory import ItemFactory
from items.rarity_enum import RarityEnum


LOOT_TABLES_PATH = Path(__file__).resolve().parents[2] / "data" / "loot_tables.csv"


@lru_cache(maxsize=None)
def _load_tables() -> dict:
    """Table name -> rarity weights, ordered to match RarityEnum."""
    tables = {}
    with open(LOOT_TABLES_PATH, newline='') as csvfile:
        for row in csv.DictReader(csvfile):
            tables[row['table']] = [int(row[rarity.name.lower()]) for rarity in RarityEnum]
    return tables


def roll_rarity(table: str) -> RarityEnum:
    tables = _load_tables()
    if table not in tables:
        raise ValueError(f"Unknown loot table: {table}")
    return random.choices(list(RarityEnum), weights=tables[table])[0]


def roll_item(table: str):
    """Roll a rarity from the table's weights, then a random item of that rarity."""
    return ItemFactory().create_random_item(roll_rarity(table))
