"""
Add "# cython: profile=True" to world.pyx before profiling
"""

import pstats
import cProfile
from yaml import safe_load
from world import World

with open("config.yml", "r") as cfg:
	config = safe_load(cfg)

world = World(config)

cProfile.runctx("world.drive(1000, 1, 0, 1)", globals(), locals(), "Profile.prof")

s = pstats.Stats("Profile.prof")
s.strip_dirs().sort_stats("time").print_stats()
