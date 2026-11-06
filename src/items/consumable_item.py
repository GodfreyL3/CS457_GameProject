import random
from pathlib import Path

from core.stats import Stat
from items.base_item import BaseItem


CONSUMABLE_DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "consumable_data.csv"


class ConsumableItem(BaseItem):
    def __init__(self, id: int):
        super().__init__(id, type="consumable")

        row = self.load_row(CONSUMABLE_DATA_PATH, id, "Consumable")
        self.load_common_fields(row)
        self.category = row['category']
        self.effect_type = row['effect_type']
        self.stat = Stat[row['stat']]
        self.effect_min = int(row['effect_min'])
        self.effect_max = int(row['effect_max'])
        self.duration = int(row['duration_turns'])
        self.target = row['target']

    def rollEffect(self):
        return random.randint(self.effect_min, self.effect_max)

    def display_info(self):
        return (f"{self.getFullName()} [{self.rarity.name}] "
                f"{self.effect_type} {self.stat.value} {self.effect_min}-{self.effect_max}")
