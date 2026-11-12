import sys
import argparse
import socket
import selectors
from src.core.connection_state import ConnectionState


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

# Enter the main event loop to handle socket events
try:
    while True:
        events = sel.select(timeout=1)
        for key, mask in events:
            state = key.data

except KeyboardInterrupt:
    print("[INFO] Client interrupted by user")
finally:
    sel.unregister(sock)
    sock.close()
    sel.close()
