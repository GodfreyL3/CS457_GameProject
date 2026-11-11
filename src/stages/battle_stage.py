import random

from entities.enemy_factory import EnemyFactory
from stages.stage import Stage


MAX_ENCOUNTER_SIZE = 3


class BattleStage(Stage):
    def __init__(self, level: int, enemies: list = None):
        super().__init__(level, enemies if enemies is not None else self._generate_enemies(level))

    @staticmethod
    def _generate_enemies(level: int) -> list:
        """1-3 random enemies for the level; a boss always fights alone."""
        factory = EnemyFactory()
        first = factory.create_random_enemy(level)
        if first.getLootTable() == "boss":
            return [first]

        extra = random.randint(0, MAX_ENCOUNTER_SIZE - 1)
        return [first] + [factory.create_random_enemy(level) for _ in range(extra)]

    def getType(self):
        return "fight"
