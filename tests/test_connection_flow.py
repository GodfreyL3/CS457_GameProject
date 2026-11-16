import selectors
import socket
import subprocess
import sys
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from unittest.mock import Mock

from src.core.connection_state import ConnectionState
from src.core.message import MessageBuffer, ProtocolMessage


ROOT = Path(__file__).resolve().parents[1]


class ConnectionFlowTests(unittest.TestCase):
    def test_queue_handles_partial_writes(self):
        selector = Mock()
        sock = Mock()
        state = ConnectionState(selector, sock, ("localhost", 12345))
        message = ProtocolMessage("CONNECT", {"player_name": "Ari"})
        encoded = message.encode()
        sock.send.side_effect = [5, BlockingIOError(), len(encoded) - 5]

        state.queue_message(message)
        state.write()
        self.assertEqual(bytes(state.send_buffer), encoded[5:])
        state.write()
        self.assertEqual(bytes(state.send_buffer), encoded[5:])
        state.write()

        self.assertEqual(state.send_buffer, bytearray())
        selector.modify.assert_called_with(sock, selectors.EVENT_READ, data=state)

    def test_server_dispatches_connect(self):
        process = subprocess.Popen(
            [sys.executable, "-u", "server.py", "-p", "0"],
            cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        )
        self.addCleanup(self.stop_process, process)
        with selectors.DefaultSelector() as selector:
            selector.register(process.stdout, selectors.EVENT_READ)
            self.assertTrue(selector.select(5), "server did not start")
        line = process.stdout.readline()
        self.assertIn("Server listening on port ", line)
        port = int(line.rsplit(" ", 1)[1])

        with socket.create_connection(("127.0.0.1", port), timeout=5) as first:
            first.sendall(ProtocolMessage(
                "CONNECT", {"player_name": "Ari"}, "connect-1"
            ).encode())
            waiting = self.receive_messages(first)[0]
            self.assertEqual(waiting.msg_type, "WAIT_FOR_PLAYERS")
            self.assertEqual(waiting.payload["reason"], "PLAYER_NOT_CONNECTED")
            self.assertEqual(waiting.payload["message"], "Waiting for one more player to connect.")

            with socket.create_connection(("127.0.0.1", port), timeout=5) as second:
                second.sendall(ProtocolMessage(
                    "CONNECT", {"player_name": "Bea"}, "connect-2"
                ).encode())
                first_reply = self.receive_messages(first)[0]
                second_reply = self.receive_messages(second)[0]

                for reply, name, number in ((first_reply, "Ari", 1), (second_reply, "Bea", 2)):
                    self.assertEqual(reply.msg_type, "CONNECT_OK")
                    self.assertEqual(reply.request_id, f"connect-{number}")
                    self.assertEqual(reply.payload["player_name"], name)
                    self.assertEqual(reply.payload["player_id"], f"p{number}")
                    self.assertEqual(reply.payload["player_num"], number)
                    client_state = ConnectionState(Mock(), Mock(), ("localhost", port))
                    with redirect_stdout(StringIO()):
                        client_state.handle_message(waiting)
                        client_state.handle_message(reply)
                    self.assertEqual(client_state.input_mode, "CLASS_CHOICE")
                    self.assertEqual(client_state.player_name, name)
                    self.assertEqual(client_state.player_id, number)

                self.assertEqual(first_reply.payload["session_id"], second_reply.payload["session_id"])
                self.assertTrue(first_reply.payload["session_id"])
                self.assertEqual(set(first_reply.payload["classes"]), {"thief", "wizard", "knight"})

                first.sendall(ProtocolMessage("CLASS_CHOICE", {"class": "KNIGHT"}).encode())
                self.assertEqual(self.receive_messages(first)[0].msg_type, "WAIT_FOR_OTHER_PLAYER")

    def test_client_sends_connect_with_prompted_name(self):
        with socket.socket() as listener:
            listener.bind(("127.0.0.1", 0))
            listener.listen()
            listener.settimeout(5)
            port = listener.getsockname()[1]
            process = subprocess.Popen(
                [sys.executable, "-u", "client.py", "-i", "127.0.0.1", "-p", str(port)],
                cwd=ROOT, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                text=True,
            )
            self.addCleanup(self.stop_process, process)
            process.stdin.write("Ari\n")
            process.stdin.flush()
            with listener.accept()[0] as connection:
                connection.settimeout(5)
                messages = self.receive_messages(connection)

        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].msg_type, "CONNECT")
        self.assertEqual(messages[0].payload, {"player_name": "Ari"})

    @staticmethod
    def receive_messages(sock):
        buffer = MessageBuffer()
        while True:
            chunk = sock.recv(4096)
            if not chunk:
                raise ConnectionError("Connection closed before a message arrived")
            messages = buffer.feed(chunk)
            if messages:
                return messages

    @staticmethod
    def stop_process(process):
        if process.poll() is None:
            process.terminate()
        process.communicate(timeout=5)

if __name__ == "__main__":
    unittest.main()
