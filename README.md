# CS457_GameProject
Game Project for Colorado State CS457 Computer Networks and the Internet

The message format supports newline-delimited JSON. `ProtocolMessage` in
`src/core/message.py` represents one message; `Message` remains an alias.
`ConnectionState` in `src/core/connection_state.py` holds the receive and send
buffers for a connection and provides method stubs for you to implement.
The client attaches this state to the selector, but its event handling is not
implemented yet.

Run the client from the project root with `python3 client.py -i HOST -p PORT`.
It prompts for a player name and sends a `CONNECT` message. Run the server with
`python3 server.py -p PORT`.
