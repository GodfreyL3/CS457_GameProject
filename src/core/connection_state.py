import selectors
from .message import MessageBuffer


def _heading(title: str) -> None:
    print(f"\n{'=' * 48}")
    print(f"  {title}")
    print("=" * 48)


def _section(title: str) -> None:
    print(f"\n  +-- {title} " + "-" * max(0, 40 - len(title)) + "+")


def _display_value(value, indent: int = 2) -> None:
    prefix = " " * indent
    if isinstance(value, dict):
        if not value:
            print(f"{prefix}(none)")
        for key, item in value.items():
            label = str(key).replace("_", " ")
            label = label if label.isupper() else label.capitalize()
            if isinstance(item, (dict, list)):
                print(f"{prefix}{label}:")
                _display_value(item, indent + 2)
            else:
                print(f"{prefix}{label}: {item}")
    elif isinstance(value, list):
        if not value:
            print(f"{prefix}(none)")
        for item in value:
            if isinstance(item, (dict, list)):
                print(f"{prefix}-")
                _display_value(item, indent + 2)
            else:
                print(f"{prefix}- {item}")
    else:
        print(f"{prefix}{value}")


class ConnectionState:
    """State belonging to one non-blocking socket connection."""

    def __init__(self, selector, sock, addr):
        self.selector = selector
        self.sock = sock
        self.addr = addr
        self.receive_buffer = MessageBuffer()
        self.send_buffer = bytearray()
        self.input_mode = "WAITING"
        self.has_turn = False
        self.available_actions = []
        self.player_id = None
        self.player_name = None
        self.area_state = None

    def process_events(self, mask):
        if mask & selectors.EVENT_READ:
            self.read()
        if mask & selectors.EVENT_WRITE:
            self.write()

    def get_input_mode(self):
        return self.input_mode

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

    def queue_message(self, message):
        self.send_buffer.extend(message.encode())
        self.selector.modify(self.sock, selectors.EVENT_READ | selectors.EVENT_WRITE, data=self)

    def write(self):
        if self.send_buffer:
            try:
                sent = self.sock.send(self.send_buffer)
                if sent == 0:
                    raise ConnectionError("Peer closed connection while sending")
                del self.send_buffer[:sent]
            except BlockingIOError:
                return

        if not self.send_buffer:
            self.selector.modify(self.sock, selectors.EVENT_READ, data=self)


    def handle_message(self, message):
        # Grab the message attributes for processing
        msg_type = message.msg_type
        content = message.payload

        # reset available actions
        self.available_actions = []

        # Implement the logic to handle the message based on its type and content
        match msg_type:
            case "CONNECT_OK":
                self.connect_ok(content)
            case "CONNECT_ERR":
                self.connect_err(content)
            case "WAIT_FOR_PLAYERS":
                self.wait_for_players(content)
            case "OTHER_PLAYER_DISCONNECTED":
                self.other_player_disconnected(content)
            case "CLASS_CHOICE_OK":
                self.class_choice_ok(content)
            case "CLASS_CHOICE_ERR":
                self.class_choice_err(content)
            case "GAME_START":
                self.game_start(content)
            case "AREA_SELECT":
                self.area_select(content)
            case "LOAD_AREA_STATE":
                self.load_area_state(content)
            case "ATTACK_ACTION":
                self.attack_action(content)
            case "DEFEND_ACTION":
                self.defend_action(content)
            case "USE_ITEM_ACTION":
                self.use_item_action(content)
            case "PICK_UP_ACTION":
                self.pick_up_action(content)
            case "GAME_OVER":
                self.game_over(content)
            case "GAME_WON":
                self.game_won(content)
            case "PROTOCOL_ERR":
                self.protocol_err(content)
            case _:
                pass

        return


    # Below will be utility methods for displaying CLI UI to user depending on the message received
    def connect_ok(self, content: dict):
        
        # Assign player name and ID from the content
        self.player_id = content["player_num"]
        self.player_name = content["player_name"]

        # Create welcome heading for the user
        _heading("CONNECTED")
        print(f"  Welcome {content['player_name']}! You are player {content['player_num']}.")
        print("\n  Choose your class:")
        print("    1. Thief")
        print("    2. Wizard")
        print("    3. Knight")
        print("\n  Enter the number corresponding to your class choice:")

        # update input mode to indicate that the client should choose a class
        self.input_mode = "CLASS_CHOICE"
        
        return



    def connect_err(self, content: dict):
        self.input_mode = "WAITING"
        _heading("CONNECTION ERROR")
        print(f"  Code: {content['code']}")
        print(f"  {content['message']}")
        return


    def wait_for_players(self, content: dict):
        # This notification can arrive while the player is choosing a class.
        _heading("WAITING FOR PLAYERS")
        print(f"  Reason: {content['reason']}")
        print(f"  {content['message']}")
        return


    def other_player_disconnected(self, content: dict):
        self.input_mode = "WAITING"
        _heading("PLAYER DISCONNECTED")
        print("  Another player has disconnected.")
        print(f"  {content['message']}")
        return


    def class_choice_ok(self, content: dict):
        self.input_mode = "WAITING"
        _heading("CLASS SELECTED")
        print(f"  Class: {content['class']}")
        print("  Starting stats:")
        _display_value(content['stats'], 4)

        if content['waiting_for_other_player']:
            print("\n  Waiting for the other player to choose their class...")


        return


    def class_choice_err(self, content: dict):
        self.input_mode = "CLASS_CHOICE"
        _heading("CLASS CHOICE ERROR")
        print(f"  {content['message']}")
        return


    def game_start(self, content: dict):
        self.input_mode = "WAITING"
        _heading("GAME START")
        print(f"  {content['message']}")
        return

    def area_select(self, content: dict):
        self.input_mode = "AREA_CHOICE"
        _heading("CHOOSE AN AREA")
        print(f"  {content['message']}")
        print("  If players disagree, the next area is selected by a coin flip.")
        for c in content["choices"]:
            print(f"    {c['choice_id']}. {c['type']} (area {c['area_number']})")
        print("\n  Enter the number corresponding to your area choice:")

        self.available_actions = content["available_actions"]
        _section("Available actions")
        for i, action in enumerate(self.available_actions, start=1):
            print(f"    {i}. {action}")

        return

    def load_area_state(self, content: dict):
        self.area_state = content
        self.input_mode = "AREA"

        # detemine if it is the player's turn
        self.has_turn = content['turn'] == self.player_id

        # Heading data
        _heading("AREA STATE")
        print(f"  Area: {content['type']}  |  Level: {content['level']}")
        print(f"  Current turn: {content['turn']}")
        print(f"  Can progress: {'Yes' if content['can_progress'] else 'No'}")

        # Display events to the player
        _section("Recent events")
        for event in content["message_stack"]:
            print(f"    - {event}")
        if not content["message_stack"]:
            print("    No recent events.")

        # Display player and game state sections
        for key, label in (
            ("player1_state", "Player 1"),
            ("player2_state", "Player 2"),
            ("cpu_states", "Enemies"),
            ("items", "Available items"),
        ):
            _section(label)
            _display_value(content[key], 4)
        print(f"\n  +{'-' * 44}+")

        # at the bottom, display the available actions for the player, add a number thgen the action
        # so the client knows which number corresponds to which action
        # dont need logic, as the server will serve up the available actions
        self.available_actions = content["available_actions"]
        _section("Available actions")
        for i, action in enumerate(self.available_actions, start=1):
            print(f"    {i}. {action}")

        

        return

    # Need to add messages for sub-menu actions (who to attck, what item to use, etc.)
    def attack_action(self, content: dict):
        self.input_mode = "ATTACK"
        _heading("CHOOSE AN ATTACK TARGET")
        print(f"  {content['message']}")
        for i, enemy in enumerate(content["enemies"], start=1):
            print(f"    {i}. {enemy['name']} (HP: {enemy['hp']})")
        
        # Save the 0 for going back to the previous menu
        print("    0. Go back")
        print("\n  Enter the number corresponding to your attack target:")

        return


    def defend_action(self, content: dict):
        self.input_mode = "DEFEND"
        _heading("CHOOSE DEFENSE TARGET")
        print(f"  {content['message']}")
        for i, enemy in enumerate(content["enemies"], start=1):
            print(f"    {i}. {enemy['name']} (HP: {enemy['hp']})")
        
        # Save the 0 for going back to the previous menu
        print("    0. Go back")
        print("\n  Enter the number corresponding to your defense target:")

        return

    def use_item_action(self, content: dict):
        self.input_mode = "USE_ITEM"
        
        # Fetch items from player's inventory
        _heading("CHOOSE AN ITEM IN INVENTORY")

        # Determine if client is player 1 or player 2
        if self.player_id == 1:
            items = content["player1_state"]["backpack"]
        else:
            items = content["player2_state"]["backpack"]

        # Display the items in the player's inventory
        for i, item in enumerate(items, start=1):
            print(f"    {i}. {item['name']} (Quantity: {item['quantity']})")
        print("\n  Enter the number corresponding to the item you want to use:")

        # Save the 0 for going back to the previous menu
        print("    0. Go back")

        return


    def pick_up_action(self, content: dict):
        self.input_mode = "PICK_UP"
        _heading("CHOOSE AN ITEM TO PICK UP")
        print(f"  {content['message']}")
        for i, item in enumerate(content["items"], start=1):
            print(f"    {i}. {item['name']} (Quantity: {item['quantity']})")

        # Save the 0 for going back to the previous menu
        print("    0. Go back")
        print("\n  Enter the number corresponding to the item you want to pick up:")

        return


    def game_over(self, content: dict):
        self.input_mode = "GAME_OVER"
        _heading("GAME OVER")
        print("  Game over.")


    def game_won(self, content: dict):
        self.input_mode = "GAME_OVER"
        _heading("VICTORY")
        print("  You won the game!")

    def protocol_err(self, content: dict):
        # A protocol error alone does not determine the current game phase.
        _heading("PROTOCOL ERROR")
        print(f"  Code: {content['code']}")
        print(f"  {content['message']}")