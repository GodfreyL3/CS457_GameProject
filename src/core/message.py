import json
import time
from dataclasses import dataclass, field
from typing import Optional

REQUIRED_FIELDS = ("msg_type", "payload", "timestamp")


@dataclass
class ProtocolMessage:
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
    def from_dict(cls, data: dict) -> "ProtocolMessage":
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
    def from_json(cls, text: str) -> "ProtocolMessage":
        try:
            return cls.from_dict(json.loads(text))
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON: {e}")

    # One message per line; json.dumps escapes newlines inside strings
    def to_line(self) -> bytes:
        return (self.to_json() + "\n").encode("utf-8")

    @classmethod
    def from_line(cls, line: bytes) -> "ProtocolMessage":
        try:
            return cls.from_json(line.decode("utf-8"))
        except UnicodeDecodeError as e:
            raise ValueError(f"Invalid UTF-8: {e}")


Message = ProtocolMessage

MAX_LINE_BYTES = 64 * 1024


class MessageBuffer:
    """Reassembles messages from raw TCP chunks, which may split or merge lines."""

    def __init__(self, max_line_bytes: int = MAX_LINE_BYTES):
        self._data = b""
        self._max = max_line_bytes

    def feed(self, chunk: bytes) -> list:
        self._data += chunk
        *lines, self._data = self._data.split(b"\n")
        if len(self._data) > self._max or any(len(l) > self._max for l in lines):
            self._data = b""
            raise ValueError("Message exceeds maximum line length")
        return [ProtocolMessage.from_line(l) for l in lines if l.strip()]

    @classmethod
    def parse_message(cls, buffer: "MessageBuffer") -> tuple:
        messages = buffer.feed(b"")
        if not messages:
            raise ProtocolMessage.IncompleteMessage()
        return messages[0], buffer

    @property
    def data(self) -> bytes:
        return self._data

    def consume(self, n: int) -> None:
        self._data = self._data[n:]
