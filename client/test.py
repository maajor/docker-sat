from satclient import SATClient

sbsar = "test/tex.sbsar"
ao = "test/low_ao.png"
pos = "test/low_position.png"
norm = "test/low_worldnormal.png"

low = "test/low.fbx"
high = "test/high.fbx"

client = SATClient('127.0.0.1:1028')
bake_outputs = client.bake(high, low, size=256)
print("Bake output: " + str(bake_outputs))

render_outputs = client.render(sbsar, ao=ao, position=pos, world_normal=norm)
print("Render output: " + str(render_outputs))
