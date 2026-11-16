import json
import unittest
from unittest.mock import patch

from entities.enemy import Enemy
from entities.player import Player
from items.consumable_item import ConsumableItem
from stages.battle_stage import BattleStage
from stages.event_stage import EventStage
from stages.shop_stage import ShopStage


class StageStateTests(unittest.TestCase):
    def setUp(self):
        self.player1 = Player("Ari", "KNIGHT")
        self.player2 = Player("Bea", "WIZARD")
        self.enemy = Enemy(1)
        self.stage = BattleStage(2, self.player1, self.player2, [self.enemy])

    def test_area_state_contains_current_game_data_and_is_json_serializable(self):
        self.player1.modifyHealth(-3)
        self.player1.modifyCoins(12)
        item = ConsumableItem(1)
        listing_id = self.stage.addItem(item, 6)
        messages = ["The fight begins"]

        state = self.stage.getStageState(
            "p1", messages
        )

        self.assertEqual(state["type"], "fight")
        self.assertEqual(state["level"], 2)
        self.assertEqual(state["turn"], "p1")
        self.assertFalse(state["can_progress"])
        self.assertEqual(state["player1_state"]["class"], "knight")
        self.assertEqual(state["player1_state"]["curr_health"], self.player1.getCurrentHealth())
        self.assertEqual(state["player1_state"]["coin"], 12)
        self.assertEqual(state["player1_state"]["r_item"]["name"], self.player1.weapon.getFullName())
        self.assertEqual(state["player2_state"]["backpack"][0]["quantity"], 1)
        self.assertEqual(state["cpu_states"]["cpu1"]["name"], self.enemy.getName())
        self.assertEqual(state["items"][str(listing_id)]["cost"], 6)
        self.assertEqual(json.loads(json.dumps(state)), state)
        messages.append("later")
        self.assertEqual(state["message_stack"], ["The fight begins"])

    def test_empty_stage_and_unequipped_player(self):
        self.stage.enemies.clear()
        self.player1.equipWeapon(None)
        self.player1.equipArmor(None)
        self.player1.backpack.clear()

        state = self.stage.getStageState("p2", [])

        self.assertTrue(state["can_progress"])
        self.assertEqual(state["cpu_states"], {})
        self.assertEqual(state["items"], {})
        self.assertIsNone(state["player1_state"]["armour"])
        self.assertIsNone(state["player1_state"]["r_item"])
        self.assertEqual(state["player1_state"]["backpack"], [])

    def test_listing_states_use_stage_prices_for_each_item_type(self):
        items = [self.player1.getArmor(), self.player1.getWeapon(), ConsumableItem(1)]
        for cost, item in enumerate(items):
            self.stage.addItem(item, cost)

        state = self.stage.getStageState("p1", [])

        for index, item in enumerate(items, start=1):
            self.assertEqual(state["items"][str(index)], {
                "name": item.getFullName(),
                "type": item.type,
                "id": item.id,
                "cost": index - 1,
            })

    def test_all_stages_use_the_players_given_at_construction(self):
        stages = [
            self.stage,
            ShopStage(2, self.player1, self.player2, stock_size=0),
            EventStage(self.player1, self.player2),
        ]
        self.player1.modifyCoins(5)
        for stage in stages:
            with self.subTest(stage=stage.getType()):
                state = stage.getStageState("p1", [])
                self.assertEqual(state["player1_state"]["coin"], 5)
                self.assertEqual(state["player2_state"]["name"], "Bea")

    def test_battle_generates_enemies_when_not_supplied(self):
        with patch.object(BattleStage, "_generate_enemies", return_value=[self.enemy]) as generate:
            stage = BattleStage(2, self.player1, self.player2)

        generate.assert_called_once_with(2)
        self.assertEqual(stage.getEnemies(), [self.enemy])


if __name__ == "__main__":
    unittest.main()
