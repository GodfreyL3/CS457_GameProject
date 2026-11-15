import sys
import argparse
import socket
import selectors

from src.core.connection_state import ConnectionState
from src.core.message import ProtocolMessage

# Handles user input from stdin
def handle_input(connection_state, line):

    if connection_state.get_input_mode() == "CLASS_CHOICE":
        # We know that only 1-3 are valid class choices
        if line not in ["1", "2", "3"]:
            print(f"[INFO] Invalid class choice: {line}")
            return

        # Get class string based on the user's choice
        class_map = {
            "1": "thief",
            "2": "wizard",
            "3": "knight"
        }
        class_choice = class_map[line]

        # Encode into Message and send
        message = ProtocolMessage(msg_type="CLASS_CHOICE", payload=class_choice)
        connection_state.write(message.encode())
        
    elif connection_state.get_input_mode() == "AREA_CHOICE":

        # We know that only 1-3 are valid area choices
        if line not in ["1", "2", "3"]:
            print(f"[INFO] Invalid area choice: {line}")
            return
        
        message = ProtocolMessage(msg_type="AREA_CHOICE", payload=line)
        connection_state.write(message.encode())
    elif connection_state.get_input_mode() == "AREA" and connection_state.has_turn:
        handle_area_input(connection_state, line)
    else:
        print(f"[INFO] Ignoring input: {line}")


def handle_area_input(connection_state, line):

    # Generate the valid turns for the current area
    valid_turns = []

    # If in a sub menu, actions will be limited based on the context
    

    # Can progress if no enemies. Held in nested dict called "cpu_states"
    if "cpu_states" in connection_state.area_state and not connection_state.area_state["cpu_states"]:
        valid_turns.append("progress")

    if connection_state.area_state["type"] == "fight":
        # In a fight, can attack if there are enemies,
        # including their teammate if theyre feeling particularly silly
        valid_turns.append("attack")
        valid_turns.append("defend")

    # you can pick up items if available in the area
    if "items" in connection_state.area_state and connection_state.area_state["items"]:
        valid_turns.append("pick_up")

    # You can use an item if you have any
    valid_turns.append("use_item")

    # Print the valid turns to show to the player
    turn_num = len(valid_turns)
    print("\n============================================")
    print("Valid turns for this area:")
    for turn in valid_turns:
        print(f"{turn_num}- {turn}")
        turn_num -= 1


    return


# Helper function to handle the attack action
def handle_attack(connection_state, line):
    
    # Ask user for the target of the attack

    #Send attack message to server

    return


def handle_defend(connection_state, line):

    # Ask user for the defense action details

    # send defend message to server

    return


def handle_use_item(connection_state, line):

    # Ask user for the item to use in their inventory

    # send use item message to server

    return


def handle_pick_up(connection_state, line):

    # Ask user for the item to pick up in the area

    # send pick up message to server

    return


def handle_event_action(connection_state, line):

    # Ask user for the event action details

    # send event action message to server

    return

# Init parser and define command-line arguments
parser = argparse.ArgumentParser(description="Client for CS457 RPG Game Project")
parser.add_argument("-i",  type=str, default="localhost", help="Game Server DNS Hostname")
parser.add_argument("-p", type=int, default=12345, help="Game Server Port")

args = parser.parse_args()

# Init selector
sel = selectors.DefaultSelector()

# Parse args and extract hostname and port,
# then resolve the hostname to an IP address
hostname = args.i
port = args.p
print(f"[INFO] Attempting to connect to game server at {hostname}:{port}....")
try:
    server_ip = socket.gethostbyname(hostname)
except socket.gaierror:
    print(f"[ERROR] Unable to resolve hostname {hostname}")
    sys.exit(1)

print(f"[INFO] ....Game server IP resolved to {server_ip}!")


# Start the connection
addr = (server_ip, port)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setblocking(False) # Set the socket to non-blocking mode
sock.connect_ex(addr) # Initiate non-blocking connection to the server
state = ConnectionState(sel, sock, addr)
events = selectors.EVENT_READ | selectors.EVENT_WRITE
sel.register(sock, events, data=state)
sel.register(sys.stdin, selectors.EVENT_READ, data="stdin") # register stdin for reading

# TODO: On Linux, register sys.stdin for selectors.EVENT_READ as well.
# Use a distinct data value so stdin events can be distinguished from socket events.

# Enter the main event loop to handle socket events
try:
    while True:
        events = sel.select(timeout=1)
        for key, mask in events:

            # Check for local input first
            if key.fileobj is sys.stdin:
                line = sys.stdin.readline().strip()

                if not line:
                    continue

                handle_input(state, line)
                continue

            # TODO: If key.fileobj is sys.stdin, read and handle the available input,
            # then continue so it isn't passed to the socket handler below.
            # An input thread and queue is another option when stdin isn't selectable.
            state = key.data

            try:
                state.process_events(mask)
            except Exception as e:
                print(f"[ERROR] Exception occurred: {e}")
                sel.unregister(key.fileobj)
                key.fileobj.close()
                continue

except KeyboardInterrupt:
    print("[INFO] Client interrupted by user")
finally:
    sel.unregister(sock)
    sock.close()
    sel.close()