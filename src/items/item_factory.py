
from items.weapon_item import WeaponItem
from items.armour_item import ArmourItem
from items.consumable_item import ConsumableItem

class ItemFactory:
    """Singleton: every ItemFactory() call returns the same shared instance."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def create_weapon(self, id: int):
        return WeaponItem(id)

    def create_armour(self, id: int):
        return ArmourItem(id)

    def create_consumable(self, id: int):
        return ConsumableItem(id)

    