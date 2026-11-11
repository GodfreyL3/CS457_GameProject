
import csv
import random

from items.weapon_item import WeaponItem, WEAPON_DATA_PATH
from items.armour_item import ArmourItem, ARMOUR_DATA_PATH
from items.consumable_item import ConsumableItem, CONSUMABLE_DATA_PATH

class ItemFactory:
    """Singleton: every ItemFactory() call returns the same shared instance."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            instance = super().__new__(cls)
            instance._load_index()
            cls._instance = instance
        return cls._instance

    def _load_index(self):
        # rarity name -> {item class: [ids]}, so random picks don't rescan the CSVs
        self._ids_by_rarity = {}
        for item_class, path in ((WeaponItem, WEAPON_DATA_PATH),
                                 (ArmourItem, ARMOUR_DATA_PATH),
                                 (ConsumableItem, CONSUMABLE_DATA_PATH)):
            with open(path, newline='') as csvfile:
                for row in csv.DictReader(csvfile):
                    rarity = row['rarity'].upper()
                    self._ids_by_rarity.setdefault(rarity, {}).setdefault(item_class, []).append(int(row['id']))

    def create_weapon(self, id: int):
        return WeaponItem(id)

    def create_armour(self, id: int):
        return ArmourItem(id)

    def create_consumable(self, id: int):
        return ConsumableItem(id)

    def create_random_item(self, rarity):
        """A random weapon, armour or consumable of the given RarityEnum.

        The category is picked first so the larger weapon catalog doesn't dominate.
        """
        ids_by_class = self._ids_by_rarity[rarity.name]
        item_class = random.choice(list(ids_by_class))
        return item_class(random.choice(ids_by_class[item_class]))
