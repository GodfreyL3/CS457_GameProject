import sys
import argparse
import socket
import selectors

from src.core.connection_state import ConnectionState
from src.core.message import ProtocolMessage

# Handles user input from stdin
def handle_input(connection_state, line):

    message = None
    if connection_state.get_input_mode() == "CLASS_CHOICE":

        # Encode into Message and send
        message = ProtocolMessage(msg_type="CLASS_CHOICE", payload=line)
    elif connection_state.get_input_mode() == "AREA_CHOICE":
        message = ProtocolMessage(msg_type="AREA_CHOICE", payload=line)
    elif connection_state.get_input_mode() == "AREA" and connection_state.has_turn:
        message = ProtocolMessage(msg_type="PLAYER_AREA_ACTION", payload=line)
    elif connection_state.get_input_mode() == "ATTACK" and connection_state.has_turn:
        message = ProtocolMessage(msg_type="PLAYER_ATTACK_ACTION", payload=line)
    elif connection_state.get_input_mode() == "DEFEND" and connection_state.has_turn:
        message = ProtocolMessage(msg_type="PLAYER_DEFEND_ACTION", payload=line)
    elif connection_state.get_input_mode() == "USE_ITEM" and connection_state.has_turn:
        message = ProtocolMessage(msg_type="PLAYER_USE_ITEM_ACTION", payload=line)
    elif connection_state.get_input_mode() == "PICK_UP" and connection_state.has_turn:
        message = ProtocolMessage(msg_type="PLAYER_PICK_UP_ACTION", payload=line)
        

    else:
        print(f"[INFO] Ignoring input: {line}")
        return

    connection_state.write(message.encode())

    return

# Init parser and define command-line arguments
parser = argparse.ArgumentParser(description="Client for CS457 RPG Game Project")
parser.add_argument("-i",  type=str, default="localhost", help="Game Server DNS Hostname")
parser.add_argument("-p", type=int, default=12345, help="Game Server Port")

args = parser.parse_args()

player_name = input("Enter your player name: ").strip()
if not player_name:
    parser.error("player name cannot be empty")

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
state.queue_message(ProtocolMessage("CONNECT", {"player_name": player_name}))

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