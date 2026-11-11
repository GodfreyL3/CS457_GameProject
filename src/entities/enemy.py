import csv
import random
from pathlib import Path

from entities.entity import Entity, RESISTED_DAMAGE_MULTIPLIER


ENEMY_DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "enemy_data.csv"


class Enemy(Entity):
    def __init__(self, id: int):
        # Load enemy data from the CSV file
        with open(ENEMY_DATA_PATH, newline='') as csvfile:
            for row in csv.DictReader(csvfile):
                if int(row['id']) == id:
                    break
            else:
                raise ValueError(f"Enemy with id {id} not found in {ENEMY_DATA_PATH}")

        super().__init__(
            name=row['name'],
            max_health=int(row['max_health']),
            constitution=int(row['CON']),
            dexterity=int(row['DEX']),
            strength=int(row['STR']),
            intelligence=int(row['INT']),
            affinity=row['affinity'],
        )
        self.id = id
        self.loot_table = row['loot_table']
        self.damage_min = int(row['damage_min'])
        self.damage_max = int(row['damage_max'])
        self.damage_type = row['damage_type']
        self.resistance = row['resistance']
        self.coin_min = int(row['coin_min'])
        self.coin_max = int(row['coin_max'])
        self.coins = self.rollCoins()

    def getLootTable(self):
        return self.loot_table

    def getResistance(self):
        return self.resistance

    def rollDamage(self):
        return random.randint(self.damage_min, self.damage_max)

    def getDamageType(self):
        return self.damage_type

    def rollCoins(self):
        return random.randint(self.coin_min, self.coin_max)

    def takeDamage(self, amount: int, damage_type: str):
        if self.evadesAttack():
            return

        if self.resistance == damage_type:
            amount *= RESISTED_DAMAGE_MULTIPLIER

        self.modifyHealth(-int(amount))

    def attack(self, target):
        if target.isAlive():
            target.takeDamage(self.rollDamage(), self.getDamageType())
