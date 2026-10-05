# Protocol Blueprint


- **Transport Protocol:** TCP
- **Serialization Format:** [JSON]
- **Framing Mechanism:** [Newline-delimited (`\n`) JSON payloads]


## Message Types

- <b>CONNECT</b>
    - Client -> Server
    - Client requests to join game room with specified alias
    ```json
    {
    "msg_type": "CONNECT",
    "request_id": "connect-001",
    "payload": {
        "player_name": "Ari"
    },
    "timestamp": 1727000000
    }
    ```

- <b>CONNECT_OK</b>
    - Server -> Client
    - Responds to Client of Successfull User Creation.
    - Also responds with data to allow user to choose their class
    ```json
    {
    "msg_type": "CONNECT_OK",
    "request_id": "connect-001",
    "payload": {
        "player_id": "p1",
        "player_num": 1,
        "session_id": "server-generated-session-id",
        "classes": {
        "thief": { "CON": 4, "DEX": 7, "STR": 2, "INT": 5 },
        "wizard": { "CON": 4, "DEX": 5, "STR": 2, "INT": 7 },
        "knight": { "CON": 5, "DEX": 4, "STR": 7, "INT": 2 }
        }
    },
    "timestamp": 1727000000
    }
    ```

- <b>CONNECT_ERR</b>
    - Server -> Client
    - Responds to Client of Unsuccessfull User Creation
    ```json
    {
    "msg_type": "CONNECT_ERR",
    "request_id": "connect-001",
    "payload": {
        "code": "GAME_FULL",
        "message": "This game already has two connected players."
    },
    "timestamp": 1727000000
    }
    ```

- <b>WAIT_FOR_PLAYERS</b>
    - Server -> Client
    - Tells the single connected client that it ios waiting for the other one
    ```json
    {
    "msg_type": "WAIT_FOR_PLAYERS",
    "payload": {
        "connected_players": 1,
        "required_players": 2,
        "reason": "PLAYER_NOT_CONNECTED",
        "message": "Waiting for one more player to connect."
    },
    "timestamp": 1727000000
    }
    ```

- <b>OTHER_PLAYER_DISCONNECTED</b>
    - Server -> Client
    - Tells the connected client that the other disconnected
    - Existing player will have option to continue or restart run
    ```json
    {
    "msg_type": "OTHER_PLAYER_DISCONNECTED",
    "payload": {
        "player_id": "p2",
        "message": "The other player disconnected."
    },
    "timestamp": 1727000000
    }
    ```
- <b>DISCONNECTED</b>
    - Client 0> Server
    - Client tells the server that the current user hs disconnected (Graceful)
    ```json
    {
    "msg_type": "DISCONNECTED",
    "payload": {
        "player_id": "p1|p2",
    },
    "timestamp": 1727000000
    }
    ```


- <b>CLASS_CHOICE</b>
    - Client -> Server
    - Client requests to use a specific class and sends to server
    ```json
    {
    "msg_type": "CLASS_CHOICE",
    "request_id": "class-001",
    "payload": {
        "class": "knight"
    },
    "timestamp": 1727000000
    }
    ```

- <b>CLASS_CHOICE_OK</b>
    - Server -> Client
    - Responds to Client of Successfull Class Assignment
    ```json
    {
    "msg_type": "CLASS_CHOICE_OK",
    "request_id": "class-001",
    "payload": {
        "class": "knight",
        "stats": { "CON": 5, "DEX": 4, "STR": 7, "INT": 2 },
        "waiting_for_other_player": true
    },
    "timestamp": 1727000000
    }
    ```

- <b>CLASS_CHOICE_ERR</b>
    - Server -> Client
    - Responds to Client of Unsuccessfull Class Assignment
    ```json
    {
    "msg_type": "CLASS_CHOICE_ERR",
    "request_id": "class-001",
    "payload": {
        "code": "INVALID_CLASS",
        "message": "Choose thief, wizard, or knight."
    },
    "timestamp": 1727000000
    }
    ```

- <b>GAME_START</b>
    - Server -> Client
    - Sends a start message to both players when both have connected
    - Will tell server to generate map here
    ```json
    {
    "msg_type": "GAME_START",
    "payload": {
        "message": "Both players are ready. Starting the run."
    },
    "timestamp": 1727000000
    }
    ```

- <b>AREA_SELECT</b>
    - Server -> Client
    - Sends a message to both clients to start a level choice
    - Can vary from 1 to 3 choices
    ```json
    {
    "msg_type": "AREA_SELECT",
    "payload": {
        "choices": [
        { "choice_id": "1", "type": "fight", "area_number": 2 },
        { "choice_id": "2", "type": "shop", "area_number": 2 },
        { "choice_id": "3", "type": "event", "area_number": 2 }
        ],
        "message": "Choose the next area."
    },
    "timestamp": 1727000000
    }
    ```

- <b>AREA_CHOICE</b>
    - Client -> Server
    - Sends the Client option for which level to go to next
    ```json
    {
    "msg_type": "AREA_CHOICE",
    "request_id": "area-002",
    "payload": {
        "choice_id": "2"
    },
    "timestamp": 1727000000
    }
    ```

- <b>LOAD_AREA_STATE</b>
    - Server -> Client
    - Server-side will load scenario
    - If both players disagree on level choice, will choose level based on "coinflip"
    - Also acts as intmediary state to be shared between turns
    - Items scavenged will have value 0, shop items will be more
    - Enemies will also have their own stats, pulled from a sheet of random enemies
    - "Levels" Can be kept pretty generic here. That way we dont have to make a whole seperate type for stores and bosses
    - CPU moves wont need to send out indivual states, just calculate moved server-side and send end level state
    - Enemies will be removed when health of them is 0. Players can only move forward is enemy list is 0
    - When enemies die, they will drop "free" items in the "shop"
    - Is there a concern for large message waste? Or is the size of JSON file negligible?
    ```json
    {
    "msg_type": "LOAD_AREA_STATE",
    "payload": {
        "type": "fight|event|shop|boss|rest",
        "level": 1-9,
        "turn": "p1|p2|cpu1|cpu2|...",
        "can_progress": false,
        "message_stack": ["..."],
        "player1_state": {
            "name": "name1",
            "class": "knight",
            "skill_pts": {
                "DEX": 4,
                "STR": 7,
                "INT": 2
            },
            "curr_health": 14,
            "max_health": 14,
            "coin": 100,
            "armour": {
                "name": "",
                "defense": "",
                "dex_bonus": "",
                "resistances": "",
            },
            "l_item": {
                "name": "",
                "damage": "",
                "skill_type": "",
                "effects": {

                }
            },
            "r_item": {
                "name": "",
                "damage": "",
                "skill_type": "",
                "effects": {

                }
            },
            "backpack": {
                
            }
        },
        "player2_state": {
            "..."
        },
        "cpu_states": {
            "..."
        },
        "items": {
            "1": {
                "name": "",
                "cost": 10,
            }
            
        }


    },
    "timestamp": 1727000000
    }
    ```

- <b>PLAYER_AREA_ACTION</b>
    - Client -> Server
    - Client sends their next action
    - Details of said action will depend on the action itself
    ```json
    {
    "msg_type": "PLAYER_AREA_ACTION",
    "payload": {
        "player_num": "1|2",
        "action": "buy|attack|heal|protect|action|sell|next_level",
        "slot": "right|left",
        "action_details": {
            "target": "p1|p2|cpu1|cpu2|..."
            ...
        }
    },
    "timestamp": 1727000000
    }
    ```

- <b>GAME OVER</b>
    - Server -> Client
    - Server send game over state to players
    ```json
    {
    "msg_type": "GAME_OVER",
    "payload": {    
        
    },
    "timestamp": 1727000000
    }
    ```

- <b>GAME_WON</b>
    - Server -> Client
    - Server send game won state to players
    ```json
    {
    "msg_type": "GAME_WON",
    "payload": {    
        
    },
    "timestamp": 1727000000
    }
    ```

- <b>PROTOCOL_ERR</b>
    - Server -> Client
    - Generic error message for bad message from client
    ```json
    {
    "msg_type": "PROTOCOL_ERR",
    "payload": {
        "code": "INVALID_MESSAGE",
        "message": "Message payload is missing the required field: action."
    },
    "timestamp": 1727000000
    }
    ```

# Wire Stream Example
```json
{"msg_type": "GAME_START","payload": {"message": "Both players are ready. Starting the run."},"timestamp": 1727000000}\n{"msg_type": "AREA_SELECT","payload": {"choices": [{ "choice_id": "1", "type": "fight", "area_number": 2 },{ "choice_id": "2", "type": "shop", "area_number": 2 },{ "choice_id": "3", "type": "event", "area_number": 2 }],"message": "Choose the next area."},"timestamp": 1727000000}\n
```

Wire Stream example of the server sending a <b>GAME_START</b> and <b>AREA_SELECT</b> message to one fo two clients at the beginning of a new game.
From here, the raw string JSON data is stored in a buffer until "\n" is found, deserializes string to change into a python dictionary, and returned as a JSON/dictionary object.

# Connection Termination & Socket Lifecycle Management

The host server is expected to run a loop that breaks off a thread to process each request coming from either client. This way, no matter what turn, a disconnect of any form can be handled without being blocked by an existing server process or a blocking ```recv()``` waiting for client input.

### Graceful Disconnect
- "<b>DISCONNECT</b>" standard message sent from client to game server
- socket object pertaining to client is uninitialized 
- Host takes note, depending on game state:
    - Will take game back to game start (```WAIT_FOR_PLAYERS```)
    - OR will wait for a reconnect until either scenario: (```OTHER_PLAYER_DISCONNECTED```)
        - Existing Player Quits -> Back to game start
        - Existing player decides to restart run -> Back to game start
        - 2nd client reconnects -> Previous level state is sent to both users and game resumes

### TCP EOF
- Host makes ```socket.recv()``` call, and gets ```b""``` back signalling TCP EOF
- socket object pertaining to client is uninitialized 
- Host takes note, depending on game state:
    - Will take game back to game start (```WAIT_FOR_PLAYERS```)
    - OR will wait for a reconnect until either scenario: (```OTHER_PLAYER_DISCONNECTED```)
        - Existing Player Quits -> Back to game start
        - Existing player decides to restart run -> Back to game start
        - 2nd client reconnects -> Previous level state is sent to both users and game resumes

### Broken Pipe (Client socket closed)
- on ```socket.send()```,  ```EPIPE``` is immediatley returned to server
- Host checks for this case/Captures ```BrokenPipeError``` thrown by thrown by ```socket.recv()```, depending on game state:
- socket object pertaining to client is uninitialized 
    - Will take game back to game start (```WAIT_FOR_PLAYERS```)
    - OR will wait for a reconnect until either scenario: (```OTHER_PLAYER_DISCONNECTED```)
        - Existing Player Quits -> Back to game start
        - Existing player decides to restart run -> Back to game start
        - 2nd client reconnects -> Previous level state is sent to both users and game resumes

### Hard Disconnect (RST Packet Arrives)
- Host checks for this case/Captures ```ConnectionResetError``` thrown by ```socket.recv()``` , depending on game state:
- socket object pertaining to client is uninitialized 
    - Will take game back to game start (```WAIT_FOR_PLAYERS```)
    - OR will wait for a reconnect until either scenario: (```OTHER_PLAYER_DISCONNECTED```)
        - Existing Player Quits -> Back to game start
        - Existing player decides to restart run -> Back to game start
        - 2nd client reconnects -> Previous level state is sent to both users and game resumes

### Hard Disconnect (RST Packet is Sent but dropped)
- Timeout is set on receiving server TCP socket. 
    - ```socket.settimeout(x)```
- Host checks for this case/Captures ```TimeoutError``` thrown by ```socket.recv()``` on timeout period, depending on game state:
- socket object pertaining to client is uninitialized 
    - Will take game back to game start (```WAIT_FOR_PLAYERS```)
    - OR will wait for a reconnect until either scenario: (```OTHER_PLAYER_DISCONNECTED```)
        - Existing Player Quits -> Back to game start
        - Existing player decides to restart run -> Back to game start
        - 2nd client reconnects -> Previous level state is sent to both users and game resumes
