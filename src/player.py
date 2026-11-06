from status_effect import StatusEffect
from classes import ThiefClass, WizardClass, KnightClass
from weapon_item import WeaponItem

class Player:
    def __init__(self, name: str, character_class: str):
        self.name = name
        if character_class == "THIEF":
            self.character_class = ThiefClass()
        elif character_class == "WIZARD":
            self.character_class = WizardClass()
        elif character_class == "KNIGHT":
            self.character_class = KnightClass()
        else:
            raise ValueError(f"Unknown character class: {character_class}")

        # init health based on constitution
        self.max_health = 10 + (2 * self.character_class.getConstitution())
        self.current_health = self.max_health

        # Add starting equipment to player attributes
        self.weapon = self.character_class.getStartingEquipment()[0]
        self.armor = self.character_class.getStartingEquipment()[1]
        self.backpack = self.character_class.getStartingEquipment()[2:]

        # Initialize other player attributes
        self.constitution = self.character_class.getConstitution()
        self.dexterity = self.character_class.getDexterity()
        self.strength = self.character_class.getStrength()
        self.intelligence = self.character_class.getIntelligence()
        self.affinity = self.character_class.getAffinity()

        self.status_effects = []


    def getName(self):
        return self.name

    def getCurrentHealth(self):
        return self.current_health

    def getMaxHealth(self):
        return self.max_health

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

    def getConstitution(self):
        return self.constitution

    def getDexterity(self):
        return self.dexterity

    def getStrength(self):
        return self.strength

    def getIntelligence(self):
        return self.intelligence

    def getAffinity(self):
        return self.affinity

    # For healing and damage effects
    def modifyHealth(self, amount: int):
        self.current_health += amount
        if self.current_health > self.max_health:
            self.current_health = self.max_health
        elif self.current_health < 0:
            self.current_health = 0

        return self.current_health

    def isAlive(self):
        return self.current_health > 0

    def getStatusEffects(self):
        return self.status_effects

    def addStatusEffect(self, effect):
        if effect not in self.status_effects:
            self.status_effects.append(effect)

    def tick(self):
        for effect in self.status_effects[:]:
            effect.tick()
            if effect.isExpired():
                self.status_effects.remove(effect)


    def removeStatusEffect(self, effect):
        if effect in self.status_effects:
            self.status_effects.remove(effect)


    # Backpack only holds consumable items
    # So when you equip, it's lost forever
    # Adds an element of permanence to equipment choices
    def equipWeapon(self, weapon):
        self.weapon = weapon

    def equipArmor(self, armor):
        self.armor = armor

    # For attacking
    def attack(self, target):
        if target.isAlive():

            # Take into account weapon damage and affinity matching
            damage = self.weapon.rollDamage()
            if self.affinity != target.getAffinity():
                damage *= 0.6

            target.modifyHealth(-damage)

    # For taking damage, considering armor resistance
    def takeDamage(self, amount: int, damage_type: str):
        if self.armor and self.armor.getResistance() == damage_type:
            amount *= 0.5
        self.modifyHealth(-amount)
    