import random
from pathlib import Path

from items.base_item import BaseItem


WEAPON_DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "weapon_data.csv"


class WeaponItem(BaseItem):
    def __init__(self, id: int):
        super().__init__(id, type="weapon")

        row = self.load_row(WEAPON_DATA_PATH, id, "Weapon")
        self.load_common_fields(row)
        self.damage_min = int(row['damage_min'])
        self.damage_max = int(row['damage_max'])
        self.damage_type = row['damage_type']
        self.affinity = row['affinity']
        self.weapon_type = row['weapon_type']
        self.range = row['range']

    def rollDamage(self):
        return random.randint(self.damage_min, self.damage_max)

    def getItemState(self):
        return {
            "name": self.getFullName(),
            "damage": {"min": self.damage_min, "max": self.damage_max},
            "damage_type": self.damage_type,
            "skill_type": self.affinity,
            "effects": {},
        }

    def display_info(self):
        return (f"{self.getFullName()} [{self.rarity.name}] "
                f"{self.damage_min}-{self.damage_max} {self.damage_type} damage")
