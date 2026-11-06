import csv
from pathlib import Path

from items.base_item import BaseItem
from items.rarity_enum import RarityEnum


ARMOUR_DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "armour_data.csv"


class ArmourItem(BaseItem):
    def __init__(self, id: int):
        super().__init__(id, type="armour")

        # Armour catalog reference: ARMOUR_DATA_PATH. CSV loading is not implemented.

        # Load armour data from the CSV file
        with open(ARMOUR_DATA_PATH, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if int(row['id']) == id:
                    self.name = row['name']
                    self.rarity = RarityEnum[row['rarity']]
                    self.prefix = row['prefix']
                    self.defense = int(row['defense'])
                    self.resistance = int(row['resistance'])
                    self.dex_bonus = int(row['dex_bonus'])
                    self.value = int(row['value'])
                    self.affinity = row['affinity']

                else:
                    raise ValueError(f"Armour with id {id} not found.")
