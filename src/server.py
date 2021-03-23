import time, os, math, json
import logging
import asyncio
import websockets
from jinja2 import Environment, FileSystemLoader
import sat

def mk_task_dir():
    current_time = str(int(time.time()))
    dir_name = "/home/{0}".format(current_time)
    if not os.path.exists(dir_name):
        os.mkdir(dir_name)
    return dir_name

async def receive_data(ws, manifest, item_name, dir_name):
    params = {}
    data = manifest[item_name]
    if 'path' in data:
        filename = os.path.basename(data['path'].replace("\\", "/"))
        item_savepath = "{0}/{1}".format(dir_name, filename)
        slice_count = await ws.recv()
        with open(item_savepath, 'wb') as file:
            for i in range(int(slice_count)):
                item_data = await ws.recv()
                file.write(item_data)
        params['entry'] = (item_name, item_savepath)
    else:
        item_data = await ws.recv()
        value = data['value']
        params['value'] = (item_name, value)
    return params

def build_config(channels, source, target, size, dir_name):
    _, size_num = size['value']
    _, channels_str = channels['value']
    _, source_path = source['entry']
    _, target_path = target['entry']
    size_ln = int(math.log2(int(size_num)))

    config_input = {}
    config_input['channels'] = []
    
    channel_names = channels_str.split(",")
    for channel in channel_names:
        channel_template = "template/{0}.txt".format(channel)
        if os.path.exists(channel_template):
            with open(channel_template, 'r') as f:
                template = f.read()
                config_input['channels'].append(template)

    config_input['source_path'] = source_path
    config_input['target_path'] = target_path
    config_input['size'] = size_ln

    env = Environment(
        loader=FileSystemLoader('/home/template')
    )
    template = env.get_template('preset.txt')
    config_json = template.render(config=config_input)
    print(config_json)
    config_path = "{0}/config.json".format(dir_name)
    with open(config_path, "w") as f:
        f.write(config_json)
    return config_path

async def handle_bake(ws):
    dir_name = mk_task_dir()

    manifest = await ws.recv()
    manifest = json.loads(manifest)
    print(manifest)

    size = await receive_data(ws, manifest, 'size', dir_name)
    channels = await receive_data(ws, manifest, 'channels', dir_name)
    target = await receive_data(ws, manifest, 'target', dir_name)
    source = await receive_data(ws, manifest, 'source', dir_name)
    config_path = build_config(channels, source, target, size, dir_name)

    try:
        proc = sat.bake(config_path, dir_name)
        std, err = proc.communicate()
        print("bake complete")
    except Exception as e:
        print(str(e))

    await ws.close()

async def handle_render(ws):
    dir_name = mk_task_dir()
    params = {'output_path':dir_name}
    params['entries'] = []
    params['values'] = []

    manifest = await ws.recv()

    for item in manifest:
        item_data = await receive_data(ws, manifest, item, dir_name)
        if 'entry' in item_data:
            params['entries'].append(item_data['entry'])
        else:
            params['values'].append(item_data['value'])
    
    sbsar_name = os.path.basename(manifest['sbsar']['path'].replace("\\", "/"))
    sbsar_path = "{0}/{1}".format(dir_name, sbsar_name)

    try:
        handle = sat.render(sbsar_path, **params)
        for result in handle.get_results():
            for output in result.outputs:
                print(output.value)
    except Exception as e:
        print(str(e))

    await ws.close()

async def hello(websocket, path):

    if path == "/bake":
        await handle_bake(websocket)
    elif path == "/render":
        await handle_render(websocket)
    else:
        name = await websocket.recv()
        print(f"< {name}")
        print(path)

        greeting = f"Hello {name}!"
        await websocket.send(greeting)
        websocket.close()

start_server = websockets.serve(hello, "0.0.0.0", 1028, max_size=2 ** 22, timeout=60, max_queue= 2 ** 10)

try:
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()
except KeyboardInterrupt:
    pass