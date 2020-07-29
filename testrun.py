from yaml import safe_load
from world import World

with open("config.yml", "r") as cfg:
	config = safe_load(cfg)
world = World(config)
world.drive(20000, 2, 1, 0)
