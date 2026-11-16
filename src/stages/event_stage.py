from items.loot import roll_item
from stages.stage import Stage


class EventStage(Stage):
    """A story encounter. It always offers one free reward, and may include enemies (an ambush)."""

    def __init__(self, player1, player2):
        super().__init__(level=1, player1=player1, player2=player2, enemies=[])
        self.description = "You encounter a mysterious event."
        self.addItem(roll_item("normal"), 0)

    def getType(self):
        return "event"

    def getDescription(self):
        return self.description
