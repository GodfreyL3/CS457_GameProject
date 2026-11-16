import sys
import argparse
import socket
import selectors

from src.core.game_state import GameState
from src.core.message import MessageBuffer
from types import SimpleNamespace


def accept_wrapper(sock):

    # Accept a new connection and register it with the selector
    conn, addr = sock.accept()
    conn.setblocking(False)

    # Register to client
    client = SimpleNamespace(addr=addr, incoming=MessageBuffer(), outgoing=bytearray())
    sel.register(conn, selectors.EVENT_READ, data=client)

parser = argparse.ArgumentParser(description="Server for CS457 RPG Game Project")
parser.add_argument("-p", type=int, default=12345, help="Server Port")
args = parser.parse_args()

# init selector and server socket
port = args.p

lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Avoid "Address already in use" error
lsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
lsock.bind(("", port))
lsock.listen()
lsock.setblocking(False)
print(f"[INFO] Server listening on port {port}")
sel = selectors.DefaultSelector()
sel.register(lsock, selectors.EVENT_READ, data=None)

game_state = GameState(sel)


try:
    while True:
        events = sel.select(timeout=None)
        for key, mask in events:

            # If the key's data is None, it means it's the listening socket
            # and we should accept a new connection
            if key.data is None:
                accept_wrapper(lsock)
            else:

                # Otherwise, it's a client socket and we should handle read/write events
                sock = key.fileobj
                client = key.data

                # If we have data to send, handle the write event first
                if mask & selectors.EVENT_WRITE:
                    try:
                        if client.outgoing:
                            sent = sock.send(client.outgoing)
                            if sent == 0:
                                raise ConnectionError("Socket closed while sending")
                            client.outgoing = client.outgoing[sent:]
                    except BlockingIOError:
                        pass
                    except ConnectionError as error:
                        print(f"[ERROR] Connection to {client.addr} lost while sending: {error}")
                        sel.unregister(sock)
                        sock.close()
                        continue

                    # Remove the write event if there's nothing left to send
                    if not client.outgoing:
                        sel.modify(sock, selectors.EVENT_READ, data=client)

                # If we have data to read, handle the read event next
                if mask & selectors.EVENT_READ:
                    try:
                        data = sock.recv(1024)
                        if data:
                            for message in client.incoming.feed(data):
                                print(f"[INFO] Received message from {client.addr}: {message.to_dict()}")
                                # TODO: Pass the message and socket to the game state.
                        else:
                            print(f"[INFO] Closing connection to {client.addr}")
                            sel.unregister(sock)
                            sock.close()
                            continue
                    except BlockingIOError:
                        pass
                    except ConnectionError as error:
                        print(f"[ERROR] Connection to {client.addr} lost while receiving: {error}")
                        sel.unregister(sock)
                        sock.close()
                        continue
                    except ValueError as error:
                        print(f"[ERROR] Invalid message from {client.addr}: {error}")
                        sel.unregister(sock)
                        sock.close()
                        continue




except KeyboardInterrupt:
    print("\n[INFO] Server shutting down")
finally:
    sel.close()
    lsock.close()