import json
import selectors
import socket

from .message import MessageBuffer, ProtocolMessage


class ConnectionState:
    """State belonging to one non-blocking socket connection."""

    def __init__(self, selector, sock, addr):
        self.selector = selector
        self.sock = sock
        self.addr = addr
        self.receive_buffer = MessageBuffer()
        self.send_buffer = MessageBuffer()

    def process_events(self, mask):
        if mask & selectors.EVENT_READ:
            self.read()
        if mask & selectors.EVENT_WRITE:
            self.write()

    def read(self):
        try:
            data = self.sock.recv(4096)
        except BlockingIOError:
            return

        if not data:
            raise ConnectionError("Peer closed connection")

        # Feed the received data into the receive buffer and process any complete messages
        new_messages = self.receive_buffer.feed(data)

        for message in new_messages:
            self.handle_message(message)

    def write(self):
        if self.send_buffer:
            try:
                sent = self.sock.send(self.send_buffer.data)
                self.send_buffer.consume(sent)
            except BlockingIOError:
                pass


    def handle_message(self, message):
        # Grab the message attributes for processing
        msg_type = message.msg_type
        msg_id = message.request_id
        content = message.payload
        timestamp = message.timestamp

        # Implement the logic to handle the message based on its type and content
        match msg_type:
            case "CONNECT_OK":
                self.connect_ok(content)
            case "CONNECT_ERR":
                pass
            case "WAIT_FOR_PLAYERS":
                pass
            case "OTHER_PLAYER_DISCONNECTED":
                pass
            case "CLASS_CHOICE_OK":
                pass
            case "CLASS_CHOICE_ERR":
                pass
            case "GAME_START":
                pass
            case "AREA_SELECT":
                pass
            case "LOAD_AREA_STATE":
                pass
            case "GAME_OVER":
                pass
            case "GAME_WON":
                pass
            case "PROTOCOL_ERR":
                pass
            case _:
                pass

        return


    # Below will be utility methods for displaying CLI UI to user depending on the message received
    def connect_ok(self, content=dict):

        print(f"Connection established successfully!\nWelcome {content.player_name}")
        print(f"You are player {content.player_num}")
        print(f"Please select your class:")
        print(f"1. Thief")
        print(f"2. Wizard")
        print(f"3. Knight")
        print(f"====================")
        print(f"Enter the number corresponding to your class choice:")

        # return here, main loop will handle input from the user
        # and write it to the socket.
        return

    def connect_err(self, content=dict):
        print(f"Connection error occurred. Code: {content.code}")
        print(f"Error message: {content.message}")
        
        return
