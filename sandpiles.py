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


def rreplace(s, r1, r2):
	return r2.join(s.rsplit(r1, 1))


# cython uses the rest of the cores more efficiently than multiprocessing can
cores_used = cpu_count() / 2

reps = 500
offsite = False

local_backup = "backups"
network_backup = "rasmus@bringebaerpai.duckdns.org:~/backups"

with open("config.yml", "r") as cfg:
	config = safe_load(cfg)

call(["cp", "config.yml", local_backup + "/"])
if offsite:
	call(["scp", "-P", "2200", "config.yml", network_backup + "/"])

worlds = []
configs = []
p0 = config["probability"]
dp = config["d_probability"]
n_worlds = config["n_runs"]
for i in range(n_worlds):
	mod_config = deepcopy(config)
	p = p0 + i * dp
	mod_config["probability"] = p
	mod_config["output"]["data"] = rreplace(config["output"]["data"], "/", f"/{i}_")
	mod_config["output"]["map"] = rreplace(config["output"]["map"], "/", f"/{i}_")
	# mod_config["input"] = rreplace(config["input"], "/", f"/{i}_")
	worlds.append(World(mod_config))
	configs.append(mod_config)


if config["input"] == "":
	print(
		"No input file specified - initiating randomly and driving to critical configurations"
	)

	def drive_to_stable_wrapper(tup):
		i, world = tup
		sys.stdout = open(f"proclogs/world{i}.out", "a", buffering=2)
		sys.stderr = open(f"proclogs/world{i}_err.out", "a", buffering=2)
		World.drive_to_stable(world)

	pool = Pool()
	for res in tqdm(pool.imap_unordered(drive_to_stable_wrapper, enumerate(worlds))):
		pass
	pool.close()
	pool.join()
	print("Criticality reached in all systems")


class Flag:
	def __init__(self):
		self.flag = False
		signal.signal(signal.SIGINT, self.change_state)

	def change_state(self, signum, frame):
		if type(current_process()) != ForkProcess:
			print("\b\b  \nExiting after batch is done (repeat to exit now)")
		signal.signal(signal.SIGINT, signal.SIG_DFL)
		self.flag = True


def drive_wrapper(tup):
	i, world = tup
	if i % cores_used:
		sys.stdout = open(f"proclogs/world{i}.out", "a", buffering=2)
		sys.stderr = open(f"proclogs/world{i}_err.out", "a", buffering=2)
		World.drive(world, reps, verbose=0)
	else:
		sys.stdout = sys.__stdout__
		sys.stderr = sys.__stderr__
		World.drive(world, reps, verbose=2, nest_tqdm=True)


c = 0
flag = Flag()
try:
	while True:
		pool = Pool(4)
		for res in tqdm(
			pool.imap_unordered(drive_wrapper, enumerate(worlds)),
			position=0,
			desc=f"Batch {c}",
			total=n_worlds,
		):
			pass
		pool.close()
		pool.join()

		for i, conf in enumerate(configs):
			call(["cp", conf["output"]["data"], "{}/{}.d".format(local_backup, i)])
			call(["cp", conf["output"]["map"], "{}/{}.m".format(local_backup, i)])
			if offsite:
				call("scp -P 2200 {}/{}.* {}/".format(local_backup, i, network_backup), shell=True)

		if flag.flag:
			break

		c += 1
except KeyboardInterrupt:
	pool.terminate()
