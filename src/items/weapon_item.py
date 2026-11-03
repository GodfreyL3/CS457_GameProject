import csv
import random

from os import name
from pathlib import Path

from items.base_item import BaseItem
from items.rarity_enum import RarityEnum


WEAPON_DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "weapon_data.csv"

class WeaponItem(BaseItem):


    def __init__(self, id:int):
        super().__init__(id, type="weapon")

        # Load weapon data from the CSV file
        with open(WEAPON_DATA_PATH, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if int(row['id']) == id:
                    self.name = row['name']
                    self.rarity = RarityEnum[row['rarity']]
                    self.prefix = row['prefix']
                    self.damage_min = int(row['damage_min'])
                    self.damage_max = int(row['damage_max'])
                    self.damage_type = row['damage_type']
                    self.value = int(row['value'])
                    self.affinity = row['affinity']
                    self.weapon_type = row['weapon_type']
                    self.range = row['range']
                    break

            # Throw if not found
            else:
                raise ValueError(f"Weapon with id {id} not found in {WEAPON_DATA_PATH}")


    def roll_damage(self):
        return random.randint(self.damage_min, self.damage_max)


    

        