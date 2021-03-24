import time, os, math, json
import logging
import asyncio
import websockets
from jinja2 import Environment, FileSystemLoader
import sat

class SATTask():

    def __init__(self, websocket):
        self.dir_name = self.mk_task_dir()
        self.websocket = websocket
        self.manifest = {}
        self.out_manifest = {}
        self.BUFFER_SIZE = 2 ** 20

    async def receive_manifest(self):
        manifest = await self.websocket.recv()
        self.manifest = json.loads(manifest)

    def mk_task_dir(self):
        current_time = str(int(time.time()))
        dir_name = "/home/{0}".format(current_time)
        if not os.path.exists(dir_name):
            os.mkdir(dir_name)
        return dir_name

    async def receive_data(self, item_name):
        params = {}
        data = self.manifest[item_name]
        if 'path' in data:
            filename = os.path.basename(data['path'].replace("\\", "/"))
            item_savepath = "{0}/{1}".format(self.dir_name, filename)
            slice_count = await self.websocket.recv()
            with open(item_savepath, 'wb') as file:
                for i in range(int(slice_count)):
                    item_data = await self.websocket.recv()
                    file.write(item_data)
            params['entry'] = (item_name, item_savepath)
        else:
            item_data = await self.websocket.recv()
            value = data['value']
            params['value'] = (item_name, value)
        return params

    async def send_data(self, item_name):
        print(item_name)
        data = self.out_manifest[item_name]
        print("send " + json.dumps(data))
        if 'path' in data:
            item_path = '{0}/{1}'.format(self.dir_name, data['path'])
            filesize = os.path.getsize(item_path)
            part_count = math.ceil(filesize/self.BUFFER_SIZE)
            print(part_count)
            await self.websocket.send(str(part_count))
            with open(item_path, "rb") as f:
                print("send " + item_path)
                if filesize < self.BUFFER_SIZE:
                    await self.websocket.send(f.read())
                else:
                    while True:
                        bytes_read = f.read(self.BUFFER_SIZE)
                        if not bytes_read:
                            break
                        await self.websocket.send(bytes_read)
        else:
            await self.websocket.send(data['value'])

    async def send_output(self):
        await self.websocket.send(json.dumps(self.out_manifest))
        for item in self.out_manifest:
            await self.send_data(item)

    async def run(self):
        raise Exception("Not Implemented")

class SATBakeTask(SATTask):

    def build_config(self, channels, source, target, size):
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
                    out_item = {'path':'bake_{0}.tga'.format(channel)}
                    self.out_manifest[channel] = out_item

        config_input['source_path'] = source_path
        config_input['target_path'] = target_path
        config_input['size'] = size_ln

        env = Environment(
            loader=FileSystemLoader('/home/template')
        )
        template = env.get_template('preset.txt')
        config_json = template.render(config=config_input)
        print(config_json)
        config_path = "{0}/config.json".format(self.dir_name)
        with open(config_path, "w") as f:
            f.write(config_json)
        return config_path

    async def run(self):
        await self.receive_manifest()

        size = await self.receive_data('size')
        channels = await self.receive_data('channels')
        target = await self.receive_data('target')
        source = await self.receive_data('source')
        config_path = self.build_config(channels, source, target, size)

        try:
            proc = sat.bake(config_path, self.dir_name)
            std, err = proc.communicate()
            await self.send_output()
            print("bake complete")
        except Exception as e:
            print('exception')
            print(str(e))

        await self.websocket.close()

class SATRenderTask(SATTask):

    def build_output(self, results):
        for result in results:
            for output in result.outputs:
                out_item = {'path':os.path.basename(output.value)}
                self.out_manifest[output.label] = out_item

    async def run(self):
        params = {'output_path':self.dir_name}
        params['entries'] = []
        params['values'] = []

        await self.receive_manifest()

        for item in self.manifest:
            item_data = await self.receive_data(item)
            if 'entry' in item_data:
                params['entries'].append(item_data['entry'])
            else:
                params['values'].append(item_data['value'])
        
        sbsar_name = os.path.basename(self.manifest['sbsar']['path'].replace("\\", "/"))
        sbsar_path = "{0}/{1}".format(self.dir_name, sbsar_name)

        try:
            handle = sat.render(sbsar_path, **params)
            self.build_output(handle.get_results())
            await self.send_output()
        except Exception as e:
            print(str(e))

        await self.websocket.close()


class SATServer():

    def __init__(self, port=1028):
        self.port = port

    async def route(self, websocket, path):
        if path == "/bake":
            task = SATBakeTask(websocket)
            await task.run()
        elif path == "/render":
            task = SATRenderTask(websocket)
            await task.run()
        else:
            name = await websocket.recv()
            print(f"< {name}")
            print(path)

            greeting = f"Hello {name}!"
            await websocket.send(greeting)
            websocket.close()

    def start(self):
        self.start_server = websockets.serve(self.route, "0.0.0.0", self.port, max_size=2 ** 22, timeout=60, max_queue= 2 ** 10)
        asyncio.get_event_loop().run_until_complete(self.start_server)
        asyncio.get_event_loop().run_forever()

try:
    server = SATServer()
    server.start()
except KeyboardInterrupt:
    pass