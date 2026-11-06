from enum import Enum


class Stat(Enum):
    """Canonical identifiers for anything an item or effect can modify.

    Values match the strings used for affinity and in the data CSVs.
    """

    HEALTH = "HEALTH"
    CON = "CON"
    DEX = "DEX"
    STR = "STR"
    INT = "INT"
