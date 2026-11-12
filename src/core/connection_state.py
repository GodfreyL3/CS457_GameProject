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
            # Attempt to read data from the socket
            data = self.sock.recv(4096)
            
            # Append received data to the receive buffer if any was read
            if data:
                self.receive_buffer.feed(data)
            else:
                # No data means the peer closed the connection
                raise ConnectionResetError("Peer closed connection")

            # Process complete messages from the receive buffer
            self.process_response()
            
        except (BlockingIOError, ConnectionResetError):
            raise ConnectionResetError("Peer closed connection")

    def write(self):
        if self.send_buffer:
            try:
                sent = self.sock.send(self.send_buffer.data)
                self.send_buffer.consume(sent)
            except BlockingIOError:
                pass


    def process_response(self):
        
        # While there is data in the receive buffer, attempt to parse complete messages
        while self.receive_buffer:
            try:
                # Attempt to parse a complete message from the receive buffer
                message, remaining = MessageBuffer.parse_message(self.receive_buffer)

                # Successfully parsed a complete message
                # also update the receive buffer to reflect remaining unprocessed data
                self.receive_buffer = remaining

                # Handle the parsed message
                self.handle_message(message)
            except ProtocolMessage.IncompleteMessage:
                break

    def handle_message(self, message):
        # Grab the message attributes for processing
        msg_type = message.type
        msg_id = message.id
        content = message.payload
        timestamp = message.timestamp

        # Implement the logic to handle the message based on its type and content
        match msg_type:
            case "CONNECT_OK":
                pass
            case "CONNECT_ERR":
                pass
            case "WAIT_FOR_PLAYERS":
                pass
            case "OTHER_PLAYER_DISCONNECTED":
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
            case "PROTOCOL_ERROR":
                pass


                
        
