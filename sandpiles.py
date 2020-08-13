from yaml import safe_load
from world import World
from subprocess import call
import signal
from copy import deepcopy
from multiprocessing.pool import Pool
from multiprocessing import cpu_count, current_process
from multiprocessing.context import ForkProcess
import sys
from tqdm import tqdm
from itertools import count


def rreplace(s, r1, r2):
	# Convenience function to replace last instance of substring
	return r2.join(s.rsplit(r1, 1))


# cython uses the rest of the cores more efficiently than multiprocessing can
cores_used = cpu_count() // 2

# Number of timesteps to run in each world per batch
reps = 500

# Directory to store backups
local_backup = "backups"

# Load config file
with open("config.yml", "r") as cfg:
	config = safe_load(cfg)

# Back up config file
call(["cp", "config.yml", local_backup + "/"])

# Lists to store worlds and their config dicts
worlds = []
configs = []

# Probability used in world 0
p0 = config["probability"]

# Probability increment
dp = config["d_probability"]
n_worlds = config["n_runs"]

# Initiate each world
for i in range(n_worlds):
	# Calculate probability to use in this world
	p = p0 + i * dp

	# Copy master config dict and modify it
	mod_config = deepcopy(config)
	mod_config["probability"] = p
	mod_config["seed"] = config["seed"] + i
	mod_config["output"]["data"] = rreplace(config["output"]["data"], "/", f"/{i}_")
	mod_config["output"]["map"] = rreplace(config["output"]["map"], "/", f"/{i}_")
	# mod_config["input"] = rreplace(config["input"], "/", f"/{i}_") # Uncomment this if the input files are individual for each world
	worlds.append(World(mod_config))
	configs.append(mod_config)

# If there is no input file supplied, each world is run to a stable configuration
if config["input"] == "":
	print(
		"No input file specified - initiating randomly and driving to critical configurations"
	)

	# Wrapper function for multiprocessing
	def drive_to_stable_wrapper(tup):
		i, world = tup
		sys.stdout = open(f"proclogs/world{i}.out", "a", buffering=2)
		sys.stderr = open(f"proclogs/world{i}_err.out", "a", buffering=2)
		World.drive_to_stable(world)

	# Create process pool and run until all worlds are stable
	pool = Pool(cores_used)
	for res in tqdm(pool.imap_unordered(drive_to_stable_wrapper, enumerate(worlds))):
		pass
	pool.close()
	pool.join()
	print("Criticality reached in all systems")


class Flag:
	# Class to handle keyboardinterrupts

	def __init__(self):
		self.flag = False
		signal.signal(signal.SIGINT, self.change_state)

	def change_state(self, signum, frame):
		# If running as the main process
		# Necessary as interrupts are sent to all processes
		if type(current_process()) != ForkProcess:
			print("\b\b  \nExiting after batch is done (repeat to exit now)")
		signal.signal(signal.SIGINT, signal.SIG_DFL)
		self.flag = True


# Wrapper function for multiprocessing
def drive_wrapper(tup):
	i, world = tup
	if i % cores_used:
		sys.stdout = open(f"proclogs/world{i}.out", "a", buffering=2)
		sys.stderr = open(f"proclogs/world{i}_err.out", "a", buffering=2)
		World.drive(world, reps, verbose=0)
	else:  # This block is only run by one process at a time, as it prints to stdout
		sys.stdout = sys.__stdout__
		sys.stderr = sys.__stderr__
		World.drive(world, reps, verbose=2, nest_tqdm=True)


flag = Flag()
try:
	for c in count():  # Infinite range
		# Create a new pool each batch and run 'reps' timesteps in each world
		pool = Pool(cores_used)
		for res in tqdm(
			pool.imap_unordered(drive_wrapper, enumerate(worlds)),
			position=0,
			desc=f"Batch {c}",
			total=n_worlds,
		):
			pass
		pool.close()
		pool.join()

		# Back up data and map files
		for i, conf in enumerate(configs):
			call(["cp", conf["output"]["data"], "{}/{}.d".format(local_backup, i)])
			call(["cp", conf["output"]["map"], "{}/{}.m".format(local_backup, i)])

		if flag.flag:
			break

except KeyboardInterrupt:
	pool.terminate()  # Kill all processes
