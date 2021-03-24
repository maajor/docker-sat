from satclient import SATClient

low = "test/low.fbx"
high = "test/high.fbx"
sbsar = "test/tex.sbsar"

client = SATClient('127.0.0.1:1028')
bake_outputs = client.bake(high, low, size=256)
print("Bake output: " + str(bake_outputs))

render_outputs = client.render(sbsar, ao=bake_outputs['ao'], position=bake_outputs['position'], world_normal=bake_outputs['worldnormal'])
print("Render output: " + str(render_outputs))
