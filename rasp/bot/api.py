import websockets

IP = "10.3.141.218"  # Replace by the Remote Compute IP
PORT = 3000
uri = f"ws://{IP}:{PORT}"


async def update_lidar(data: list[float]):
    async with websockets.connect(uri + "/lidar") as websocket:
        data = list(map(str, data))
        data = "[" + ",".join(data) + "]"
        await websocket.send("set$=$" + data)


async def update_log(data: str):
    async with websockets.connect(uri + "/log") as websocket:
        await websocket.send("update$=$[" + data + "]")


async def get_last_command() -> list[str] or None:
    # connect to /cmd endpoint and listen for commands
    # check if message is received
    # if yes, return it

    async with websockets.connect(uri + "/cmd") as websocket:
        await websocket.send("get$=$")
        resp = await websocket.recv()
        if resp == "None" or resp == "error" or resp == "":
            return None
        else:
            cmd = resp.split("$=$")[0]
            args = list(map(float,resp.split("$=$")[1].replace("[", "").replace("]", "").split(",")))
            return cmd, args



"""
Minji
"""

""" """

""" list of connected people
"""                    
CONNECTIONS_STATE = set()

#actual state of the robot
current_state = {
    "pins": {},
    "position": {},
    "current_action" : "",
    "action_list": [],
}

async def send_state_to_clients():
    #actual state of connected clients
    while True:
        
        state_message = json.dumps(current_state)

        #go threw the list of connected clients
        for client in CONNECTIONS_STATE:
            await client.send(state_message)
        await asyncio.sleep(1)

#retreive information 
def get_state(key=None):
    if key is None:
        return current_state
    if key in current_state:
        return {key: current_state[key]}
    return None

#define the state for a specific key
def set_state(key, value):
    if key in current_state: 
        current_state[key] = value
        return f"La cl2 '{key} a été modifiée en '{value}'."
    return f"La cle '{key}' n'existe pas dans l'etat."

#update with new infos
def update_state(data):
    current_state.update(data)

#def update_state(data):
    #update data with recieved informations
 #   state = load_state_from_file()
  #  state.update(data)
   # with open('state.json','w') as file:
    #    json.dump(state, file)





async def handle_state_ws(websocket, path):
    #to add new connected clients
    CONNECTIONS_STATE.add(websocket)

    #sending the current state of the client at the time of connection
    
    state_message = json.dumps(current_state)
    await websocket.send(state_message)

    try:
        async for message in websocket:
            try:
                data=json.loads(message)
                operation = data.get("operation")
                key = data.get("key")

                if operation =="get":
                    #get a state of a specific key
                    response = get_state(key)
                    await websocket.send(json.dumps(response))
                elif operation =="set" and key:
                    #modify state of a speficif key 
                    new_value = data.get("value")
                    await websocket.send(json.dumps(response))
                elif operation == "update" and key:
                    #update with new infos
                    new_data = data.get("data")
                    update_state(new_data)
                else:
                    await websocket.send("error : operation non valide")
            except json.JSONDecodeError:
                await websocket.send("error: message non valide")
    except json.JSONDecodeError:
            await websocket.send("error: message non valide")
    finally: 
        #delete deconnected clients from the list
        CONNECTIONS_STATE.remove(websocket)



    

def load_state_from_file():
    try:
        with open('state.json', 'r') as file:
            state = json.load(file)
    except FileNotFoundError:
        state = current_state 
        #charge default value if the document does not exist
    return state

if __name__ == "__main__":
    current_state = load_state_from_file()
    
    
    #run the server websocket
    start_server = websockets.serve(handle_state_ws, "0.0.0.0", 3000)
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.ensure_future(send_state_to_clients())
    asyncio.get_event_loop().run_forever()
