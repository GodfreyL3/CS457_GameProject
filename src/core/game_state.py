import selectors

from entities.player import Player

from .message import MessageBuffer, ProtocolMessage




# Enum states
class Mode:
    WAIT_FOR_PLAYERS = 1
    CHARACTER_SELECTION = 2
    AREA_SELECTION = 3
    AREA_STATE = 4
    PLAYER_TURN = 5
    CPU_TURN = 6
    ATTACK_STATE = 7
    DEFEND_STATE = 8
    USE_ITEM_STATE = 9
    PICK_ITEM_STATE = 10
    GAME_OVER = 11
    CONNECTION_LOST = 12

class GameState:

    def __init__(self, selector):

        # Player objects
        self.player1 = None
        self.player2 = None
        self.p1_name = None
        self.p2_name = None
        self.p1_socket = None
        self.p2_socket = None

        # Send and recive buffer
        self.selector = selector
        self.receive_buffer = MessageBuffer()
        # Game state
        self.mode = Mode.WAIT_FOR_PLAYERS


    def queue_message(self, player_num, message):

        # determine the target socket based on player number
        if player_num == 1:
            target_socket = self.p1_socket
        elif player_num == 2:
            target_socket = self.p2_socket
        else:

            # just return, we shoudnt be queuing a message for an invalid player number
            return

        # also make sure that the socket exists,
        # otherwise do nothing
        if target_socket is None:
            return

        # Get the selector key for the target socket
        key = self.selector.get_key(target_socket)

        # Get the client outgoing buffer
        client = key.data

        # Append the encoded message to the client's outgoing buffer
        client.outgoing.extend(message.encode())

        # Modify socket for writing
        self.selector.modify(target_socket, selectors.EVENT_READ | selectors.EVENT_WRITE, data=client)

        return


    # Dispatcher function for processing turns/messages
    def procress_turn(self, message: ProtocolMessage, socket=None):

        # deconstruct the message and update the game state accordingly
        message_type = message.msg_type
        payload = message.payload

        try:

            if message_type == "CONNECT":
                self.process_connect_msg(message, socket)

            elif message_type == "CHARACTER_SELECTION":
                self.process_class_selection_msg(message, socket)


        except Exception as e:
            return f"ERROR: {str(e)}"


    def process_connect_msg(self, message: ProtocolMessage, socket=None):

        # Return error if Gamestate not waiting for players
        if self.mode != Mode.WAIT_FOR_PLAYERS:
            return "ERROR: Game already in progress"

        # Assign socket and name to the first available player slot
        if self.p1_socket is None:
            self.p1_socket = socket
            self.p1_name = message.payload.get("name")
        elif self.p2_socket is None:
            self.p2_socket = socket
            self.p2_name = message.payload.get("name")

        # If both player sockets are connected, transition to character selection mode
        if self.p1_socket and self.p2_socket:
            self.mode = Mode.CHARACTER_SELECTION

        # Send connections back to both by writing to the send buffer
        # Add class selection prompt for both players
        if self.mode == Mode.WAIT_FOR_PLAYERS:
            self.queue_message(1, ProtocolMessage("WAIT_FOR_PLAYERS", {}))
            self.queue_message(2, ProtocolMessage("WAIT_FOR_PLAYERS", {}))
        else:
            send_payload = {
                "player_id": "p1",
                "player_num": 1,
                "classes": {
                    "thief": { "CON": 4, "DEX": 7, "STR": 2, "INT": 5 },
                    "wizard": { "CON": 4, "DEX": 5, "STR": 2, "INT": 7 },
                    "knight": { "CON": 5, "DEX": 4, "STR": 7, "INT": 2 }
                }
            }
            # Class Dict

            self.queue_message(1, ProtocolMessage("CONNECT_OK", send_payload))
            self.queue_message(2, ProtocolMessage("CONNECT_OK", send_payload))

        return

    def process_class_selection_msg(self, message: ProtocolMessage, socket=None):

        # Get message payload
        payload = message.payload

        # Determine socket and corresponding player
        player_num = 1 if socket == self.p1_socket else 2

        # Deconstruct the payload and update the player objects accordingly
        if self.mode != Mode.CHARACTER_SELECTION:
            self.queue_message(player_num, ProtocolMessage("ERR", {"message": "Not in character selection mode"}))
            return

        # Update the player object based on the player number
        if player_num == 1:
            self.player1 = Player(name=self.p1_name, character_class=payload.get("class"))
        else:
            self.player2 = Player(name=self.p2_name, character_class=payload.get("class"))

        # Transition to area selection mode if both players have selected their classes
        if self.player1 and self.player2:
            self.mode = Mode.AREA_SELECTION

            self.queue_message(1, ProtocolMessage("AREA_SELECTION", {}))
            self.queue_message(2, ProtocolMessage("AREA_SELECTION", {}))
        else:
            self.queue_message(player_num, ProtocolMessage("WAIT_FOR_OTHER_PLAYER", {"reason": "Waiting for the other player to select a class"}))

        return