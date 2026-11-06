import csv
import random
from pathlib import Path

from entities.enemy import Enemy, ENEMY_DATA_PATH


LEVEL_TIERS_PATH = Path(__file__).resolve().parents[2] / "data" / "level_tiers.csv"

TIERS = ("weak", "normal", "elite", "boss")


class EnemyFactory:
    """Singleton: every EnemyFactory() call returns the same shared instance."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            instance = super().__new__(cls)
            instance._load_data()
            cls._instance = instance
        return cls._instance

    def _load_data(self):
        # Enemy ids grouped by loot tier, so random picks don't rescan the CSV
        self._ids_by_tier = {tier: [] for tier in TIERS}
        with open(ENEMY_DATA_PATH, newline='') as csvfile:
            for row in csv.DictReader(csvfile):
                self._ids_by_tier[row['loot_table']].append(int(row['id']))

        # Level -> tier weights, e.g. {1: [90, 10, 0, 0], ...}
        self._tier_weights = {}
        with open(LEVEL_TIERS_PATH, newline='') as csvfile:
            for row in csv.DictReader(csvfile):
                self._tier_weights[int(row['level'])] = [int(row[tier]) for tier in TIERS]

        self.max_level = max(self._tier_weights)

    def create_enemy(self, id: int):
        return Enemy(id)

    def create_random_enemy(self, level: int):
        """Pick a tier using the level's weights, then a random enemy from that tier."""
        if level < 1:
            raise ValueError(f"Level must be at least 1, got {level}")

        # Levels past the table reuse the hardest row
        weights = self._tier_weights[min(level, self.max_level)]
        tier = random.choices(TIERS, weights=weights)[0]
        return Enemy(random.choice(self._ids_by_tier[tier]))
