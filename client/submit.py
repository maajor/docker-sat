import json
import os
from websocket import create_connection

class SATClient:
    def __init__(self, url='127.0.0.1:1028'):
        self.endpoint = "ws://{0}".format(url)

    def _collect_outputs(self, ws):
        result_manifest = ws.recv()
        result_temp = {}
        for result_item in result_manifest['items']:
            result =  ws.recv()
            with open(result_item['name'], 'wb') as file:
                file.write(result)
        ws.close()
        return result_temp

    def _send_inputs(self, ws, manifest):
        ws.send(json.dumps(manifest))
        for item in manifest:
            if 'path' in manifest[item]:
                item_path = manifest[item]['path']
                with open(item_path, "rb") as f:
                    ws.send_binary(f.read())
            else:
                item_value = manifest[item]['value']
                ws.send(item_value)

    def bake(self, highmesh_path, lowmesh_path, channels=['normal', 'ao', 'position', 'worldnormal'], size=2048):
        manifest = {
            "size": {'value' : size},
            "channels": {'value' : ",".join(channels)},
            "source": {'path' : highmesh_path},
            "target": {'path' : lowmesh_path}
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
        

