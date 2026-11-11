import sys
import argparse
import socket
import json
from core.message import Message

# Init parser and define command-line arguments
parser = argparse.ArgumentParser(description="Client for CS457 RPG Game Project")
parser.add_argument("-h", "--help", action="help", help="Show this help message and exit")
parser.add_argument("-i",  type=str, default="localhost", help="Game Server DNS Hostname")
parser.add_argument("-p", type=int, default=12345, help="Game Server Port")

args = parser.parse_args()

# Print help and exit if -h or --help is specified or if required arguments are missing
if args.h or args.i is None or args.p is None:
    parser.print_help()
    sys.exit(0)

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

client_socket = None
try:
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.settimeout(5)  # Set a timeout for the connection attempt
    client_socket.connect((server_ip, port))
    print(f"[INFO] Successfully connected to game server at {server_ip}:{port}")
except socket.error as e:
    print(f"[ERROR] Failed to connect to game server: {e}")
    sys.exit(1)

# Ask the player for their name
print("[INFO] Please enter your player name:")
player_name = input("> ")

# Format into Message JSON
connect_msg = Message(msg_type="connect", payload={"player_name": player_name})

# Send the player name to the server
try:
    client_socket.sendall(player_name.encode())
except socket.error as e:
    print(f"[ERROR] Failed to send player name to server: {e}")
    client_socket.close()
    sys.exit(1)

# Enter the main game loop for the client
while True:
    try:


        
        
    except KeyboardInterrupt:
        print("\n[INFO] Exiting game client.")
        client_socket.close()
        sys.exit(0)
    except socket.error as e:
        print(f"[ERROR] Connection error: {e}")
        client_socket.close()
        sys.exit(1)
