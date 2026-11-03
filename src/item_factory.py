
from items.weapon_item import WeaponItem

class ItemFactory:
    def create_weapon(self, id: int):
        return WeaponItem(id, "weapon")