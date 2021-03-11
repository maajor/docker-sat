import time, os
import logging
import asyncio
import websockets
import sat

async def handle_bake(ws):
    current_time = str(int(time.time()))
    dir_name = "/home/{0}".format(current_time)
    if not os.path.exists(dir_name):
        os.mkdir(dir_name)

    await ws.send("Bake Init")
    low = await ws.recv()
    lowname = "/home/{0}/low.fbx".format(current_time)
    with open(lowname, 'wb') as file:
        file.write(low)

    high = await ws.recv()
    highname = "/home/{0}/high.fbx".format(current_time)
    with open(highname, 'wb') as file:
        file.write(high)
    
    config = await ws.recv()
    configname = "/home/{0}/config.json".format(current_time)
    with open(configname, 'wb') as file:
        file.write(config)

    await ws.send("Bake Start")
    try:
        proc = sat.bake(configname, dir_name)
        stdout, stderr = proc.communicate()
        print(stdout)
        await ws.send("Bake Finished")
    except Exception as e:
        print(str(e))
        await ws.send("Bake Failed")

    await ws.close()

async def hello(websocket, path):

    if path == "/bake":
        await handle_bake(websocket)
    else:
        name = await websocket.recv()
        print(f"< {name}")
        print(path)

        greeting = f"Hello {name}!"

        await websocket.send(greeting)
        await asyncio.sleep(10)

        greeting = f"Hello Again {name}!"
        await websocket.send(greeting)

        print(f"> {greeting}")

start_server = websockets.serve(hello, "localhost", 1028)

try:
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()
except KeyboardInterrupt:
    pass