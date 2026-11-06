from pathlib import Path

from items.base_item import BaseItem


ARMOUR_DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "armour_data.csv"


class ArmourItem(BaseItem):
    def __init__(self, id: int):
        super().__init__(id, type="armour")

        row = self.load_row(ARMOUR_DATA_PATH, id, "Armour")
        self.load_common_fields(row)
        self.defense = int(row['defense'])
        self.dex_bonus = int(row['dex_bonus'])
        # Damage type this armour resists, or "none"
        self.resistance = row['resistance']
        self.slot = row['slot']
        self.affinity = row['affinity']

    def getResistance(self):
        return self.resistance

    def getDexBonus(self):
        return self.dex_bonus

    def display_info(self):
        return (f"{self.getFullName()} [{self.rarity.name}] "
                f"DEF {self.defense}, resists {self.resistance}")


