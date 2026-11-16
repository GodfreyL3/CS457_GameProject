import random

from core.stats import Stat
from entities.entity import Entity, AFFINITY_MISMATCH_MULTIPLIER, RESISTED_DAMAGE_MULTIPLIER
from entities.character_classes import ThiefClass, WizardClass, KnightClass
from items.item_factory import ItemFactory
from items.weapon_item import WeaponItem
from items.armour_item import ArmourItem
from items.consumable_item import ConsumableItem


class Player(Entity):
    def __init__(self, name: str, character_class: str):
        if character_class == "THIEF":
            char_class = ThiefClass()
        elif character_class == "WIZARD":
            char_class = WizardClass()
        elif character_class == "KNIGHT":
            char_class = KnightClass()
        else:
            raise ValueError(f"Unknown character class: {character_class}")

        # Health is based on constitution
        super().__init__(
            name=name,
            max_health=10 + (2 * char_class.getConstitution()),
            constitution=char_class.getConstitution(),
            dexterity=char_class.getDexterity(),
            strength=char_class.getStrength(),
            intelligence=char_class.getIntelligence(),
            affinity=char_class.getAffinity(),
        )
        self.character_class = char_class

        # Starting equipment is stored as catalog IDs: weapon, armour, then consumables
        factory = ItemFactory()
        weapon_id, armour_id, *consumable_ids = char_class.getStartingEquipment()
        self.weapon = factory.create_weapon(weapon_id)
        self.armor = factory.create_armour(armour_id)
        self.backpack = [factory.create_consumable(i) for i in consumable_ids]

    # Base stat + status effects (from Entity) + armour bonus
    def getDexterity(self):
        dex = super().getDexterity()
        if self.armor:
            dex += self.armor.getDexBonus()
        return dex

    def getDefense(self):
        defense = self.armor.defense if self.armor else 0
        return defense + self.getEffectBonus(Stat.DEFENSE)

    def getWeapon(self):
        return self.weapon

    def getArmor(self):
        return self.armor

    def getBackpack(self):
        return self.backpack

    def backpackContains(self, item):
        return item in self.backpack

    def getCharacterClass(self):
        return self.character_class

    def getPlayerState(self):
        armor = self.getArmor()
        weapon = self.getWeapon()
        return {
            "name": self.getName(),
            "class": type(self.getCharacterClass()).__name__.removesuffix("Class").lower(),
            "skill_pts": {
                "CON": self.getConstitution(),
                "DEX": self.getDexterity(),
                "STR": self.getStrength(),
                "INT": self.getIntelligence(),
            },
            "curr_health": self.getCurrentHealth(),
            "max_health": self.getMaxHealth(),
            "coin": self.getCoins(),
            "armour": armor.getItemState() if armor else None,
            "l_item": None,
            "r_item": weapon.getItemState() if weapon else None,
            "backpack": [item.getItemState() for item in self.getBackpack()],
        }

    # Consumables go to the backpack, weapons and armour are equipped
    def receiveItem(self, item):
        if isinstance(item, ConsumableItem):
            self.backpack.append(item)
        elif isinstance(item, WeaponItem):
            self.equipWeapon(item)
        elif isinstance(item, ArmourItem):
            self.equipArmor(item)
        else:
            raise TypeError(f"Cannot receive item of type {type(item).__name__}")

    # Backpack only holds consumable items
    # So when you equip, it's lost forever
    # Adds an element of permanence to equipment choices
    def equipWeapon(self, weapon):
        self.weapon = weapon

    def equipArmor(self, armor):
        self.armor = armor

    # Damage and resistance come from equipment
    def rollDamage(self):
        return self.weapon.rollDamage()

    def getDamageType(self):
        return self.weapon.damage_type

    def getResistance(self):
        return self.armor.getResistance() if self.armor and self.armor.getResistance() != "none" else None

    def takeDamage(self, amount: int, damage_type: str):
        if self.evadesAttack():
            return

        # Armour defense is applied with a random factor, and can't heal
        amount = max(0, amount - self.getDefense() * random.random())

        if self.getResistance() == damage_type:
            amount *= RESISTED_DAMAGE_MULTIPLIER

        self.modifyHealth(-int(amount))

    def attack(self, target):
        if target.isAlive():
            damage = self.rollDamage()
            if self.affinity != target.getAffinity():
                damage *= AFFINITY_MISMATCH_MULTIPLIER
            target.takeDamage(int(damage), self.getDamageType())
