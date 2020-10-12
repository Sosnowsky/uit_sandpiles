from world import World
from yaml import safe_load

with open("ex_config.yml", "r") as cfg:
    config = safe_load(cfg)

# Initiate world
world = World(config)

# Drive world
world.drive(100, verbose=2, animate=True, graph=True)
# world.drive_to_stable()
