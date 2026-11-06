from entities.entity import Entity
from entities.character_classes import ThiefClass, WizardClass, KnightClass
from items.weapon_item import WeaponItem

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

        # health is based on constitution
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

        # Add starting equipment to player attributes
        self.weapon = self.character_class.getStartingEquipment()[0]
        self.armor = self.character_class.getStartingEquipment()[1]
        self.backpack = self.character_class.getStartingEquipment()[2:]

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
        return self.armor.getResistance() if self.armor else None
