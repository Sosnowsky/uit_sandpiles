import pstats, cProfile
from world import World
from yaml import safe_load

with open("config.yml", "r") as cfg:
	config = safe_load(cfg)

world = World(config)

cProfile.runctx("world.drive(100, 0, 0, 0)", globals(), locals(), "Profile.prof")

s = pstats.Stats("Profile.prof")
s.strip_dirs().sort_stats("time").print_stats()