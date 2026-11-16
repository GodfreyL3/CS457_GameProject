from items.loot import roll_item
from stages.stage import Stage


SHOP_STOCK_SIZE = 5


class ShopStage(Stage):
    """Sells a fixed stock at each item's catalog value."""

    def __init__(self, level: int, player1, player2, stock_size: int = SHOP_STOCK_SIZE):
        super().__init__(level, player1, player2)
        for _ in range(stock_size):
            item = roll_item("shop")
            self.addItem(item, item.value)

    def getType(self):
        return "shop"
