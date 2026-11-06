from random import random

from entities.entity import Entity
from entities.character_classes import ThiefClass, WizardClass, KnightClass
from items.item_factory import ItemFactory

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

        # Starting equipment is stored as catalog IDs: weapon, armour, then consumables
        factory = ItemFactory()
        weapon_id, armour_id, *consumable_ids = self.character_class.getStartingEquipment()
        self.weapon = factory.create_weapon(weapon_id)
        self.armor = factory.create_armour(armour_id)
        self.backpack = [factory.create_consumable(i) for i in consumable_ids]


    def getDexterity(self):

        # Get initial dex from base dexterity and armor bonus
        dex = self.dexterity + self.armor.getDexBonus()

        # Add from effect bonuses if any
        for effect in self.active_effects:
            if effect.getStat() == "DEXTERITY":
                dex += effect.getAmount()

        return dex

    def getStrength(self):

        # Get initial strength from base strength and armor bonus
        strength = self.strength

        # Add from effect bonuses if any
        for effect in self.active_effects:
            if effect.getStat() == "STRENGTH":
                strength += effect.getAmount()

        return strength

    def getIntelligence(self):

        # Get initial intelligence from base intelligence and armor bonus
        intelligence = self.intelligence

        # Add from effect bonuses if any
        for effect in self.active_effects:
            if effect.getStat() == "INTELLIGENCE":
                intelligence += effect.getAmount()

        return intelligence

    def getDefense(self):

        # Get initial defense from armor, if exists
        defense = 0
        if self.armor:
            defense += self.armor.defense

        # Add from effect bonuses if any
        for effect in self.active_effects:
            if effect.getStat() == "DEFENSE":
                defense += effect.getAmount()

        return defense

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


    def takeDamage(self, amount: int, damage_type: str):

        # Calculate evasion chance based on dexterity
        if random.random() < (self.getDexterity() * 2) / 100:
            return

        # apply defense from armor, random factor included
        if self.armor:
            amount -= self.armor.defense * random()

        # add resistance modifier based on armor
        if self.armor and self.armor.getResistance() == damage_type:
            amount *= 0.7


        self.modifyHealth(-int(amount))

    def attack(self, target):
        if target.isAlive():
            damage = self.rollDamage()
            if self.affinity != target.getAffinity():
                damage *= 0.6
            target.takeDamage(int(damage), self.getDamageType())