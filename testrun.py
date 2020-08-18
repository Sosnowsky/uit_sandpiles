from yaml import safe_load
from world import World

# Load config file
with open("ex_config.yml", "r") as cfg:
	config = safe_load(cfg)

# Initiate world
world = World(config)

# Drive world
world.drive(10000, animate=1, graph=1)
# world.drive_to_stable()
