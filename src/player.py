from classes import ThiefClass, WizardClass, KnightClass

class Player:
    def __init__(self, name: str, character_class: str):
        self.name = name
        if character_class == "Thief":
            self.character_class = ThiefClass()
        elif character_class == "Wizard":
            self.character_class = WizardClass()
        elif character_class == "Knight":
            self.character_class = KnightClass()
        else:
            raise ValueError(f"Unknown character class: {character_class}")

        # init health based on constitution
        self.max_health = 10 + (2 * self.character_class.getConstitution())
        self.current_health = self.max_health

        # Add starting equipment to player attributes
        self.starting_weapon = self.character_class.getStartingEquipment()[0]
        self.starting_armor = self.character_class.getStartingEquipment()[1]
        self.backpack = self.character_class.getStartingEquipment()[2:]


    def getCurrentHealth(self):
        return self.current_health

    def getMaxHealth(self):
        return self.max_health

    def getStartingWeapon(self):
        return self.starting_weapon

    def getStartingArmor(self):
        return self.starting_armor

    def getBackpack(self):
        return self.backpack

    def backpackContains(self, item):
        return item in self.backpack