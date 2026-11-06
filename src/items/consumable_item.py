import csv
from pathlib import Path

from items.base_item import BaseItem
from items.rarity_enum import RarityEnum


CONSUMABLE_DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "consumable_data.csv"


class ConsumableItem(BaseItem):
    def __init__(self, id: int):
        super().__init__(id, type="consumable")

        # Load consumable data from the CSV file
        with open(CONSUMABLE_DATA_PATH, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if int(row['id']) == id:
                    self.name = row['name']
                    self.rarity = RarityEnum[row['rarity']]
                    self.prefix = row['prefix']
                    self.effect_type = row['effect_type']
                    self.effect_min = int(row['effect_min'])
                    self.effect_max = int(row['effect_max'])
                    self.duration = int(row['duration_turns'])
                    self.value = int(row['value'])
                else:
                    raise ValueError(f"Consumable with id {id} not found.")
