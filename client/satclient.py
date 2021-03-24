import json, os, math, time
from websocket import create_connection

class SATClient:
    def __init__(self, url='127.0.0.1:1028'):
        self.endpoint = "ws://{0}".format(url)
        if not os.path.exists('/temp'):
            os.mkdir('/temp')
        self.BUFFER_SIZE = 2 ** 20

    def __mk_task_dir(self):
        current_time = str(int(time.time()))
        dir_name = "/temp/{0}".format(current_time)
        if not os.path.exists(dir_name):
            os.mkdir(dir_name)
        return dir_name

    def _collect_outputs(self, ws):
        dir_name = self.__mk_task_dir()
        result_manifest = ws.recv()
        result_manifest = json.loads(result_manifest)
        result_temp = {}
        for result_item in result_manifest:
            data = result_manifest[result_item]
            if 'path' in data:
                item_savepath = "{0}/{1}".format(dir_name, data['path'])
                slice_count = ws.recv()
                with open(item_savepath, 'wb') as file:
                    for i in range(int(slice_count)):
                        item_data = ws.recv()
                        file.write(item_data)
                result_temp[result_item] = item_savepath
            else:
                item_data = ws.recv()
                result_temp[result_item] = item_data
        ws.close()
        return result_temp

    def _send_inputs(self, ws, manifest):
        ws.send(json.dumps(manifest))
        for item in manifest:
            if 'path' in manifest[item]:
                item_path = manifest[item]['path']
                filesize = os.path.getsize(item_path)
                part_count = math.ceil(filesize/self.BUFFER_SIZE)
                ws.send(str(part_count))
                with open(item_path, "rb") as f:
                    i = 0
                    if filesize < self.BUFFER_SIZE:
                        ws.send_binary(f.read())
                    else:
                        while True:
                            bytes_read = f.read(self.BUFFER_SIZE)
                            if not bytes_read:
                                break
                            ws.send_binary(bytes_read)
                            i+=1
            else:
                item_value = manifest[item]['value']
                ws.send(str(item_value))

    def bake(self, highmesh_path, lowmesh_path, channels=['normal', 'ao', 'position', 'worldnormal'], size=2048):
        manifest = {
            "size": {'value' : size},
            "channels": {'value' : ",".join(channels)},
            "target": {'path' : lowmesh_path},
            "source": {'path' : highmesh_path}
        }

        ws = create_connection("{0}/bake".format(self.endpoint))
        self._send_inputs(ws, manifest)
        return self._collect_outputs(ws)

    def render(self, sbsar_path, **inputs):
        manifest = {
            "sbsar": {'path': sbsar_path}
        }
        for input_name in inputs:
            val = inputs[input_name]
            if os.path.exists(val):
                data = {"path":val}
            else:
                data = {"value":val}
            manifest[input_name] = data

        ws = create_connection("{0}/render".format(self.endpoint))
        self._send_inputs(ws, manifest)
        return self._collect_outputs(ws)
        

