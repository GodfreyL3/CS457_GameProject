from random import random
import selectors
from uuid import uuid4

from entities.player import Player
from stages.event_stage import EventStage
from stages.shop_stage import ShopStage
from stages.battle_stage import BattleStage

from .message import MessageBuffer, ProtocolMessage




# Enum states
class Mode:
    WAIT_FOR_PLAYERS = 1
    CLASS_SELECTION = 2
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
        

        # Holds temp player data (e.g., name) before character selection
        self.p1_data = None
        self.p2_data = None
        self.p1_request_id = None
        self.p2_request_id = None
        self.session_id = str(uuid4())

        # Holds the sockets for each player
        self.p1_socket = None
        self.p2_socket = None

        # Send and recive buffer
        self.selector = selector
        self.receive_buffer = MessageBuffer()
        # Game state
        self.mode = Mode.WAIT_FOR_PLAYERS

        # ===== GAME STATE VARIABLES =====
        self.available_areas = [] # Can hold the list of areas available next
        self.area = None # holds the current area being played

        # Player objects representing the two players in the game
        self.player1 = None
        self.player2 = None

        # Objects representing the stage and level and total stages passed
        self.stage = 1
        self.level = 1
        self.total_stages_passed = 0


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
                return self.process_connect_msg(message, socket)

            elif message_type == "CLASS_CHOICE":
                self.process_class_selection_msg(message, socket)

            elif message_type == "AREA_CHOICE":
                self.process_area_choice_msg(message, socket)

            elif message_type == "PLAYER_AREA_ACTION":
                self.process_player_area_action_msg(message, socket)

            elif message_type == "PLAYER_ATTACK_ACTION":
                self.process_player_attack_action_msg(message, socket)

            elif message_type == "PLAYER_DEFEND_ACTION":
                self.process_player_defend_action_msg(message, socket)

            elif message_type == "PLAYER_USE_ITEM_ACTION":
                self.process_player_use_item_action_msg(message, socket)

            elif message_type == "PLAYER_PICK_UP_ACTION":
                self.process_player_pick_up_action_msg(message, socket)


        except Exception as e:
            return f"ERROR: {str(e)}"


    def process_connect_msg(self, message: ProtocolMessage, socket=None):

        # Return error if Gamestate not waiting for players
        if self.mode != Mode.WAIT_FOR_PLAYERS:
            return "ERROR: Game already in progress"

        # Assign socket and name to the first available player slot
        if self.p1_socket is None:
            self.p1_socket = socket
            self.p1_data = message.payload.get("player_name")
            self.p1_request_id = message.request_id
        elif self.p2_socket is None:
            self.p2_socket = socket
            self.p2_data = message.payload.get("player_name")
            self.p2_request_id = message.request_id

        # If both player sockets are connected, transition to character selection mode
        if self.p1_socket and self.p2_socket:
            self.mode = Mode.CLASS_SELECTION

        # Send connections back to both by writing to the send buffer
        # Add class selection prompt for both players
        if self.mode == Mode.WAIT_FOR_PLAYERS:
            self.queue_message(1, ProtocolMessage("WAIT_FOR_PLAYERS", {
                "connected_players": 1,
                "required_players": 2,
                "reason": "PLAYER_NOT_CONNECTED",
                "message": "Waiting for one more player to connect.",
            }))
        else:
            classes = {
                "thief": { "CON": 4, "DEX": 7, "STR": 2, "INT": 5 },
                "wizard": { "CON": 4, "DEX": 5, "STR": 2, "INT": 7 },
                "knight": { "CON": 5, "DEX": 4, "STR": 7, "INT": 2 }
            }
            for player_num, name, request_id in (
                (1, self.p1_data, self.p1_request_id),
                (2, self.p2_data, self.p2_request_id),
            ):
                send_payload = {
                    "player_id": f"p{player_num}",
                    "player_num": player_num,
                    "player_name": name,
                    "session_id": self.session_id,
                    "classes": classes,
                }
                self.queue_message(
                    player_num, ProtocolMessage("CONNECT_OK", send_payload, request_id)
                )

        return

    def process_class_selection_msg(self, message: ProtocolMessage, socket=None):

        # Get message payload
        payload = message.payload

        # Determine socket and corresponding player
        player_num = 1 if socket == self.p1_socket else 2

        # Deconstruct the payload and update the player objects accordingly
        if self.mode != Mode.CLASS_SELECTION:
            self.queue_message(player_num, ProtocolMessage("ERR", {"message": "Not in class choice mode"}))
            return

        # Update the player object based on the player number
        if player_num == 1:
            self.player1 = Player(name=self.p1_data, character_class=payload.get("class"))
        else:
            self.player2 = Player(name=self.p2_data, character_class=payload.get("class"))

        # Transition to area selection mode if both players have selected their classes
        if self.player1 and self.player2:
            self.mode = Mode.AREA_SELECTION

            # Use rand to generate 3 random areas between a fight, shop, or event
            self.available_areas = [random.choice(["fight", "shop", "event"]) for _ in range(3)]

            # Generate payload
            payload = {"choices": [
                {"choice_id": "1", "type": self.available_areas[0]},
                {"choice_id": "2", "type": self.available_areas[1]},
                {"choice_id": "3", "type": self.available_areas[2]}
            ]}

            # Empty the temp data
            self.player1_data = None
            self.player2_data = None

            # Send to both players the area selection choices
            self.queue_message(1, ProtocolMessage("AREA_SELECTION", payload))
            self.queue_message(2, ProtocolMessage("AREA_SELECTION", payload))
        else:
            self.queue_message(player_num, ProtocolMessage("WAIT_FOR_OTHER_PLAYER", {"reason": "Waiting for the other player to select a class"}))

        return

    def process_area_choice_msg(self, message: ProtocolMessage, socket=None):

        # Determine player number based on socket
        if socket != self.p1_socket and socket != self.p2_socket:
            self.queue_message(1, ProtocolMessage("ERR", {"message": "Invalid socket connection"}))
            return

        # Determine the player number based on the socket connection
        player_num = 1 if socket == self.p1_socket else 2

        # Extract the choice num from the message payload
        choice_id = message.payload.get("choice_id")

        # Validate the choice_id
        if choice_id not in ["1", "2", "3"]:
            self.queue_message(player_num, ProtocolMessage("ERR", {"message": "Invalid area choice"}))
            return

        # Store players choice 
        if player_num == 1:
            self.player1_data = choice_id
        else:
            self.player2_data = choice_id

        if self.player1_data is not None and self.player2_data is not None:
            # Both players have made their choices, determine the next area
            area1 = self.available_areas[int(self.player1_data) - 1]
            area2 = self.available_areas[int(self.player2_data) - 1]

            # If both payers selected different areas, do a coin flip to determine which area to use
            if area1 != area2:
                chosen_area = random.choice([area1, area2])
                area1 = chosen_area
                area2 = chosen_area

            # Consolidate the chosen area as the current area for the game
            self.area = area1
    
            # Now fetch the type, and have the stage generate the appropriate content based on the area type
            area_type = self.area
            if area_type == "fight":
                self.stage = BattleStage(self.level, self.player1, self.player2)
            elif area_type == "shop":
                # Randomize stock size
                stock_size = random.randint(1, 5)
                self.stage = ShopStage(self.level, self.player1, self.player2, stock_size)
            elif area_type == "event":
                self.stage = EventStage(self.player1, self.player2)

        else:
            self.queue_message(player_num, ProtocolMessage("WAIT_FOR_OTHER_PLAYER", {"reason": "Waiting for the other player to select an area"}))



    def process_player_area_action_msg(self, message: ProtocolMessage, socket=None):
        pass

    def process_player_attack_action_msg(self, message: ProtocolMessage, socket=None):
        pass

    def process_player_defend_action_msg(self, message: ProtocolMessage, socket=None):
        pass

    def process_player_use_item_action_msg(self, message: ProtocolMessage, socket=None):
        pass

    def process_player_pick_up_action_msg(self, message: ProtocolMessage, socket=None):
        pass