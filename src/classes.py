class BaseClass:
    """Character-class stats and starting equipment."""

    def __init__(
        self,
        constitution: int = 0,
        dexterity: int = 0,
        strength: int = 0,
        intelligence: int = 0
    ) -> None:
        self.constitution = constitution
        self.dexterity = dexterity
        self.strength = strength
        self.intelligence = intelligence
        self.starting_equipment = []
        

    def getConstitution(self) -> int:
        return self.constitution

    def getDexterity(self) -> int:
        return self.dexterity

    def getStrength(self) -> int:
        return self.strength

    def getIntelligence(self) -> int:
        return self.intelligence

    def getAffinity(self) -> str:
        return self.affinity

    def getStartingEquipment(self) -> list[str]:
        return self.starting_equipment


class ThiefClass(BaseClass):
    def __init__(self) -> None:
        super().__init__(constitution=4, dexterity=7, strength=2, intelligence=5)
        self.affinity = "DEX"

        # Starting equipment for Thief
        self.starting_equipment = ["Starting Dagger", "Starting Leather Armor", "Health Potion", "Health Potion"]  # Example starting equipment for Thief


class WizardClass(BaseClass):
    def __init__(self) -> None:
        super().__init__(constitution=4, dexterity=5, strength=2, intelligence=7)
        self.affinity = "INT"

        # Starting equipment for Wizard
        self.starting_equipment = ["Starting Staff", "Starting Robe", "Health Potion", "Health Potion"]  # Example starting equipment for Wizard


class KnightClass(BaseClass):
    def __init__(self) -> None:
        super().__init__(constitution=5, dexterity=4, strength=7, intelligence=2)
        self.affinity = "STR"

        # Starting equipment for Knight
        self.starting_equipment = ["Starting Sword", "Starting Plate Armor", "Health Potion", "Health Potion"]  # Example starting equipment for Knight
