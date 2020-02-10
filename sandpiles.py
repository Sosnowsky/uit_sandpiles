from yaml import safe_load
from world import World

config = dict()
with open('config.yml') as cfg:
	config = safe_load(cfg)

world = World(config)
