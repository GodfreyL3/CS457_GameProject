import json
import time
from dataclasses import dataclass, field
from typing import Optional

REQUIRED_FIELDS = ("msg_type", "payload", "timestamp")


@dataclass
class Message:
    msg_type: str
    payload: dict = field(default_factory=dict)
    request_id: Optional[str] = None
    timestamp: int = field(default_factory=lambda: int(time.time()))

    def to_dict(self) -> dict:
        data = {
            "msg_type": self.msg_type,
            "request_id": self.request_id,
            "payload": self.payload,
            "timestamp": self.timestamp,
        }
        # Server-initiated messages have no request_id, so leave it out
        if self.request_id is None:
            del data["request_id"]
        return data

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: dict) -> "Message":
        if not isinstance(data, dict):
            raise ValueError("Message must be a JSON object")
        missing = [f for f in REQUIRED_FIELDS if f not in data]
        if missing:
            raise ValueError(f"Message missing fields: {', '.join(missing)}")
        if not isinstance(data["payload"], dict):
            raise ValueError("Message payload must be a JSON object")
        return cls(
            msg_type=data["msg_type"],
            payload=data["payload"],
            request_id=data.get("request_id"),
            timestamp=data["timestamp"],
        )

    @classmethod
    def from_json(cls, text: str) -> "Message":
        try:
            return cls.from_dict(json.loads(text))
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON: {e}")
