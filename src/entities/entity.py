import random
from abc import ABC, abstractmethod

from core.stats import Stat


# Damage multiplier when attacker and target affinities differ
AFFINITY_MISMATCH_MULTIPLIER = 0.6
# Damage multiplier when the target resists the incoming damage type
RESISTED_DAMAGE_MULTIPLIER = 0.7
# Evasion chance gained per point of dexterity
EVASION_PER_DEX = 0.02


class Entity(ABC):
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
        self.coins = 0
        self.status_effects = []

    def getName(self):
        return self.name

    def getCurrentHealth(self):
        return self.current_health

    def getMaxHealth(self):
        return self.max_health

    def getAffinity(self):
        return self.affinity

    # Stat getters include bonuses from active status effects
    def getCoins(self):
        return self.coins

    def modifyCoins(self, amount: int):
        self.coins = max(0, self.coins + amount)
        return self.coins

    def getConstitution(self):
        return self.constitution + self.getEffectBonus(Stat.CON)

    def getDexterity(self):
        return self.dexterity + self.getEffectBonus(Stat.DEX)

    def getStrength(self):
        return self.strength + self.getEffectBonus(Stat.STR)

    def getIntelligence(self):
        return self.intelligence + self.getEffectBonus(Stat.INT)

    def getEffectBonus(self, stat: Stat):
        return sum(e.getAmount() for e in self.status_effects if e.getStat() == stat)

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

    def evadesAttack(self):
        return random.random() < self.getDexterity() * EVASION_PER_DEX

    def getResistance(self):
        return None

    # Hooks for subclasses: where damage comes from differs
    @abstractmethod
    def rollDamage(self) -> int:
        pass

    @abstractmethod
    def getDamageType(self) -> str:
        pass

    @abstractmethod
    def takeDamage(self, amount: int, damage_type: str):
        pass

    @abstractmethod
    def attack(self, target):
        pass
