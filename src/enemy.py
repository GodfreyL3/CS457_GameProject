import csv
import random
from pathlib import Path


ENEMY_DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "enemy_data.csv"


class Enemy:
    def __init__(self, id: int):
        self.id = id

        # Load enemy data from the CSV file
        with open(ENEMY_DATA_PATH, newline='') as csvfile:
            for row in csv.DictReader(csvfile):
                if int(row['id']) == id:
                    self.name = row['name']
                    self.loot_table = row['loot_table']
                    self.max_health = int(row['max_health'])
                    self.constitution = int(row['CON'])
                    self.dexterity = int(row['DEX'])
                    self.strength = int(row['STR'])
                    self.intelligence = int(row['INT'])
                    self.affinity = row['affinity']
                    self.damage_min = int(row['damage_min'])
                    self.damage_max = int(row['damage_max'])
                    self.damage_type = row['damage_type']
                    self.resistance = row['resistance']
                    self.coin_min = int(row['coin_min'])
                    self.coin_max = int(row['coin_max'])
                    break
            else:
                raise ValueError(f"Enemy with id {id} not found in {ENEMY_DATA_PATH}")

        self.current_health = self.max_health
        self.status_effects = []

    def getName(self):
        return self.name

    def getLootTable(self):
        return self.loot_table

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

    def getResistance(self):
        return self.resistance

    def modifyHealth(self, amount: int):
        self.current_health = max(0, min(self.max_health, self.current_health + amount))
        return self.current_health

    def isAlive(self):
        return self.current_health > 0

    def rollDamage(self):
        return random.randint(self.damage_min, self.damage_max)

    def rollCoins(self):
        return random.randint(self.coin_min, self.coin_max)

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

    # Matches Player.takeDamage so either side can be a target
    def takeDamage(self, amount: int, damage_type: str):
        if self.resistance == damage_type:
            amount = int(amount * 0.5)
        self.modifyHealth(-amount)

    def attack(self, target):
        if target.isAlive():
            target.takeDamage(self.rollDamage(), self.damage_type)
