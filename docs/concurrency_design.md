# Concurrency Design

## Concurrency Model Selection: Non-Blocking I/O Multiplexing
For this project, I feel that Non-Blocking I/O would make the most sense to implement for this project. Since this game is turn based for both players and the server (who is also a "player" in this case), I/O multiplexing lets the server handle multiple clients without dedicating a thread to each one.

### Initializing/Accepting a new client socket
At first initialization, the server program will listen to all addresses coming in on a certain port (lets use 61616 for an example). It will bind to 0.0.0.0:61616 and be set to listen and to not block, so incoming connections can be accepted as they arrive.

#### Example:
```python
HOST = "0.0.0.0"
PORT = 9003

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()
server.setblocking(False)

inputs = [server]
outputs = []
message_queues = {}

players = []

while inputs:
    for s in readable:
        if s is server:
            conn, addr = server.accept()
            conn.setblocking(False)
            inputs.append(conn)
            message_queues[conn] = []
```

### Client Registration
To further differentiate client connections to the server, each client will have a unique player name and ID. A Player object will be created server-side with all the data needed to hold a player's state.

### Game loop servicing
The game as stated before will be turn-based. That being said, player and server moves will always be sequential. However, this does not stop the clients themselves from sending messages when it's not their turn; the server will just validate and reject anything that is out of order.

### Client Teardown
If a client leaves gracefully, their associated socket will be removed from the monitored sockets, and closed for any future messages. This event will happen when the socket is readable with the appropriate disconnect signal.

## Thread Safety
Because this game is cooperative and the need for hiding intent is not needed, no data will be hidden from either client during this game. Both will share the Level number, level state (enemies, events, rewards), and turn order.

## Sequence Diagram

```mermaid
sequenceDiagram
    autonumber
    participant P1 as Player 1
    participant S as Server
    participant P2 as Player 2

    Note over P1,P2: Example: two players join, defeat a goblin, and choose the next area
    P1->>S: CONNECT (name: Ari)
    S-->>P1: CONNECT_OK (player: p1, available classes)
    S-->>P1: WAIT_FOR_PLAYERS
    P2->>S: CONNECT (name: Bea)
    S-->>P2: CONNECT_OK (player: p2, available classes)
    S->>S: Enter CHARACTER_SELECT
    P1->>S: CLASS_CHOICE (thief)
    S-->>P1: CLASS_CHOICE_OK
    P2->>S: CLASS_CHOICE (knight)
    S-->>P2: CLASS_CHOICE_OK
    S-->>P1: GAME_START
    S-->>P2: GAME_START
    S->>S: Generate next area choices

    S-->>P1: AREA_SELECT (fight or shop)
    S-->>P2: AREA_SELECT (fight or shop)
    P1->>S: AREA_CHOICE (fight)
    S-->>P1: AREA_CHOICE_OK
    P2->>S: AREA_CHOICE (fight)
    S-->>P2: AREA_CHOICE_OK
    S->>S: Generate fight and calculate DEX order
    Note over S: Example order: P1, goblin, P2
    S-->>P1: AREA_STATE (P1's turn, goblin: 8 HP)
    S-->>P2: AREA_STATE (P1's turn, goblin: 8 HP)

    opt Player 2 attempts an early action
        P2->>S: PLAYER_AREA_ACTION (attack goblin)
        S-->>P2: ACTION_ERR (NOT_YOUR_TURN)
        Note over S: State and turn remain unchanged
    end

    P1->>S: PLAYER_AREA_ACTION (attack goblin)
    S->>S: Validate action, apply 4 damage, select next actor
    S-->>P1: AREA_STATE (goblin: 4 HP, CPU turn)
    S-->>P2: AREA_STATE (goblin: 4 HP, CPU turn)

    S->>S: Resolve goblin attack and select next actor
    S-->>P1: AREA_STATE (attack result, P2's turn)
    S-->>P2: AREA_STATE (attack result, P2's turn)

    P2->>S: PLAYER_AREA_ACTION (attack goblin)
    S->>S: Validate action, defeat goblin, create 0-coin drop
    S->>S: Select next actor and allow progression
    S-->>P1: AREA_STATE (P1's turn, drop available, can_progress: true)
    S-->>P2: AREA_STATE (P1's turn, drop available, can_progress: true)

    P1->>S: PLAYER_AREA_ACTION (progress)
    S->>S: Validate zero enemies and resolve area
    Note over S: No rank-up in this example
    S-->>P1: AREA_SELECT (next destinations)
    S-->>P2: AREA_SELECT (next destinations)

    opt Unexpected disconnect while choosing the next area
        P2->>S: TCP connection closes or heartbeat times out
        S->>S: Enter CONNECTION_LOST, pause run, preserve state
        S-->>P1: PLAYER_DISCONNECTED (choose wait or abandon)
        alt Player 1 chooses to abandon
            P1->>S: DISCONNECT_CHOICE (abandon)
            S->>S: Abandon run and return to WAIT_FOR_PLAYERS
            S-->>P1: RUN_ABANDONED
            S-->>P1: WAIT_FOR_PLAYERS
        else Player 1 chooses to wait
            P1->>S: DISCONNECT_CHOICE (wait)
            S-->>P1: WAIT_FOR_RECONNECT
            Note over P1,S: Run stays paused
            P2->>S: RECONNECT (session credentials)
            S->>S: Validate reconnect and restore Player 2's session
            S-->>P2: RECONNECT_OK
            S->>S: Resume preserved area selection
            S-->>P1: AREA_SELECT (preserved choices and vote status)
            S-->>P2: AREA_SELECT (preserved choices and vote status)
        end
    end
```
