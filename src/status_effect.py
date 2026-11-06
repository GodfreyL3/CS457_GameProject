import random

from stats import Stat


class StatusEffect:
    def __init__(self, name: str, stat: Stat, amount: int, turns_left: int, chance: float = 1.0):
        if not 0.0 <= chance <= 1.0:
            raise ValueError(f"chance must be between 0.0 and 1.0, got {chance}")
        self.name = name
        self.stat = stat
        # Positive buffs/heals, negative debuffs/damage
        self.amount = amount
        self.turns_left = turns_left
        # Probability (0.0-1.0) the effect lands when applied; offensive effects use < 1.0
        self.chance = chance

    def getName(self):
        return self.name

    def getStat(self):
        return self.stat

    def getAmount(self):
        return self.amount

    def getTurnsLeft(self):
        return self.turns_left

    def getChance(self):
        return self.chance

    def roll(self):
        """Returns True if the effect should be applied."""
        return random.random() < self.chance

    def tick(self):
        """Advance one turn; returns True while the effect is still active."""
        if self.turns_left > 0:
            self.turns_left -= 1
        return self.isActive()

    def isActive(self):
        return self.turns_left > 0

    def __repr__(self):
        return f"StatusEffect({self.name!r}, {self.stat.value}, {self.amount:+d}, {self.turns_left} turns, {self.chance:.0%})"
