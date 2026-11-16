from abc import ABC, abstractmethod
from dataclasses import dataclass
import random

from entities.player import Player
from items.base_item import BaseItem
from items.loot import roll_item


@dataclass
class StageItem:
    """An item listed for sale; cost 0 means it was dropped and is free to take."""

    item: BaseItem
    cost: int


class Stage(ABC):
    """One area of a run. Players may advance once no enemies remain."""

    def __init__(self, level: int, player1: Player, player2: Player, enemies: list = None):
        self.level = level
        self.player1 = player1
        self.player2 = player2
        self.enemies = list(enemies) if enemies else []
        
        # Listing id -> StageItem; ids are never reused so players can't buy the wrong item
        self.items = {}
        self._next_listing_id = 1

        # Turn num
        self.turn_num = 0

        # Turn list
        initiative_order = []  # List of (entity, initiative_roll) tuples, sorted by initiative descending

        # With players and enemies, roll for first turn
        # Much like in DND, roll a 10 + or - DEX level / 2
        p1_roll = random.randint(1, 10) + (self.player1.getDexterity() // 2)
        initiative_order.append((self.player1, p1_roll))
        p2_roll = random.randint(1, 10) + (self.player2.getDexterity() // 2)
        initiative_order.append((self.player2, p2_roll))

        # And now enemies same way as players, roll initiative based on DEX or similar stat
        for enemy in self.enemies:  
            enemy_roll = random.randint(1, 10) + (enemy.getDexterity() // 2)
            initiative_order.append((enemy, enemy_roll))

        # Sort initiative order descending
        initiative_order.sort(key=lambda x: x[1], reverse=True)
        self.initiative_order = [entity for entity, _ in initiative_order]

    @abstractmethod
    def getType(self) -> str:
        """Stage type as named in the protocol: fight, shop or event."""

    def getLevel(self):
        return self.level

    def getEnemies(self):
        return self.enemies

    def getItems(self):
        return self.items

    def addItem(self, item, cost: int) -> int:
        listing_id = self._next_listing_id
        self._next_listing_id += 1
        self.items[listing_id] = StageItem(item, cost)
        return listing_id

    def canProgress(self) -> bool:
        return not any(enemy.isAlive() for enemy in self.enemies)

    # Remove dead enemies; each one drops a free item based on its loot tier
    # and pays its full coins to every player passed in
    def removeDefeatedEnemies(self, players=()) -> list:
        defeated = [enemy for enemy in self.enemies if not enemy.isAlive()]
        for enemy in defeated:
            self.enemies.remove(enemy)
            for player in players:
                player.modifyCoins(enemy.getCoins())
            self.addItem(roll_item(enemy.getLootTable()), 0)
        return defeated

    def buy(self, player, listing_id: int):
        if listing_id not in self.items:
            raise ValueError(f"No item with listing id {listing_id}")

        listing = self.items[listing_id]
        if player.getCoins() < listing.cost:
            raise ValueError(f"Not enough coins: need {listing.cost}, have {player.getCoins()}")

        player.modifyCoins(-listing.cost)
        player.receiveItem(listing.item)
        del self.items[listing_id]
        return listing.item

    def nextTurn(self):
        self.turn_num += 1

    def getStageState(self, message_stack):
        """Return the LOAD_AREA_STATE payload using the current game context."""
        
        # Can always use an item from the backpack
        available_actions = []
        available_actions.append("use_item")

        # Can always attack if there are enemies alive
        if any(enemy.isAlive() for enemy in self.enemies):
            available_actions.append("attack")

        # Can always defend
        available_actions.append("defend")

        # Can always pick up items if there are any available
        if self.items:
            available_actions.append("pick_up")

        # Can always progress if all enemies are defeated
        if self.canProgress():
            available_actions.append("progress")

        
        return {
            "type": self.getType(),
            "level": self.getLevel(),
            "turn_num": self.turn_num,
            "turn": self.initiative_order[self.turn_num % len(self.initiative_order)],
            "can_progress": self.canProgress(),
            "message_stack": list(message_stack),
            "player1_state": self.player1.getPlayerState(),
            "player2_state": self.player2.getPlayerState(),
            "cpu_states": {
                f"cpu{index}": enemy.getEnemyState()
                for index, enemy in enumerate(self.enemies, start=1)
            },
            "items": {
                str(listing_id): {
                    **listing.item.getListingState(),
                    "cost": listing.cost,
                }
                for listing_id, listing in self.items.items()
            },
            "available_actions": list(available_actions),
        }
