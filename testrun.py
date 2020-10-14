from world import World
from yaml import safe_load

with open("ex_config.yml", "r") as cfg:
    config = safe_load(cfg)

# Initiate world
world = World(config)

# Drive world
world.drive(50000, verbose=2, animate=False, graph=False)
# world.drive_to_stable()
