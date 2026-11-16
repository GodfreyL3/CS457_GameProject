import csv
from abc import ABC, abstractmethod
from pathlib import Path

from items.rarity_enum import RarityEnum


class BaseItem(ABC):
    def __init__(self, id: int, type: str):
        self.id = id
        self.type = type

    @staticmethod
    def load_row(data_path: Path, id: int, label: str) -> dict:
        """Return the CSV row with the given id, or raise ValueError if absent."""
        with open(data_path, newline='') as csvfile:
            for row in csv.DictReader(csvfile):
                if int(row['id']) == id:
                    return row
        raise ValueError(f"{label} with id {id} not found in {data_path}")

    def load_common_fields(self, row: dict):
        """Fields every item catalog shares."""
        self.name = row['name']
        self.rarity = RarityEnum[row['rarity'].upper()]
        self.prefix = row['prefix']
        self.value = int(row['value'])

    def getFullName(self) -> str:
        return f"{self.prefix} {self.name}"

    def getListingState(self):
        return {
            "name": self.getFullName(),
            "type": self.type,
            "id": self.id,
        }

    @abstractmethod
    def display_info(self):
        pass
