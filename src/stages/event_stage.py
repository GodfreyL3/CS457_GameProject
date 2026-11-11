from items.loot import roll_item
from stages.stage import Stage


class EventStage(Stage):
    """A story encounter. It always offers one free reward, and may include enemies (an ambush)."""

    def __init__(self, level: int, description: str = "", enemies: list = None):
        super().__init__(level, enemies)
        self.description = description
        self.addItem(roll_item("normal"), 0)

    def getType(self):
        return "event"

    def getDescription(self):
        return self.description
