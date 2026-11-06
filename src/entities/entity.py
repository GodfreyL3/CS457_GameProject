import random

# Damage multiplier when attacker and target affinities differ
AFFINITY_MISMATCH_MULTIPLIER = 0.6
RESISTED_DAMAGE_MULTIPLIER = 0.5


class Entity:
    """Shared base for anything that can fight: players and enemies."""

    def __init__(self, name: str, max_health: int, constitution: int, dexterity: int,
                 strength: int, intelligence: int, affinity: str):
        self.name = name
        self.max_health = max_health
        self.current_health = max_health
        self.constitution = constitution
        self.dexterity = dexterity
        self.strength = strength
        self.intelligence = intelligence
        self.affinity = affinity
        self.status_effects = []

    def getName(self):
        return self.name

    def getCurrentHealth(self):
        return self.current_health

    def getMaxHealth(self):
        return self.max_health

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
        self.current_health = max(0, min(self.max_health, self.current_health + amount))
        return self.current_health

    def isAlive(self):
        return self.current_health > 0

    def getStatusEffects(self):
        return self.status_effects

    def addStatusEffect(self, effect):
        if effect not in self.status_effects:
            self.status_effects.append(effect)

    def removeStatusEffect(self, effect):
        if effect in self.status_effects:
            self.status_effects.remove(effect)

    def tick(self):
        for effect in self.status_effects[:]:
            effect.tick()
            if not effect.isActive():
                self.status_effects.remove(effect)

    # Hooks for subclasses: where damage and resistance come from differs
    def rollDamage(self) -> int:
        raise NotImplementedError

    def getDamageType(self):
        raise NotImplementedError

    def getResistance(self):
        return None

    # For taking damage, considering resistance
    def takeDamage(self, amount: int, damage_type: str):
        if self.getResistance() == damage_type:
            amount *= RESISTED_DAMAGE_MULTIPLIER

        # also take into account dex for possible evasion
        evasion_chance = self.getDexterity() * 2 / 100
        if random.random() < evasion_chance:
            amount = 0
        
        self.modifyHealth(-int(amount))

    # For attacking, taking into account affinity matching
    def attack(self, target):
        if target.isAlive():
            damage = self.rollDamage()
            if self.affinity != target.getAffinity():
                damage *= AFFINITY_MISMATCH_MULTIPLIER
            target.takeDamage(int(damage), self.getDamageType())
