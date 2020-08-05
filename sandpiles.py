from yaml import safe_load
from world import World
from subprocess import call
from tqdm import tqdm
import signal
from copy import deepcopy


def rreplace(s, r1, r2):
	return r2.join(s.rsplit(r1, 1))


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
	mod_config["input"] = rreplace(config["input"], "/", f"/{i}_")
	worlds.append(World(mod_config))
	configs.append(mod_config)


if config["input"] == "":
	print(
		"No input file specified - initiating randomly and driving to critical configurations"
	)
	for world in worlds:
		world.drive_to_stable()


class Flag:
	def __init__(self):
		self.flag = False
		signal.signal(signal.SIGINT, self.change_state)

	def change_state(self, signum, frame):
		progress_print(string="Exit flag set to True (repeat to exit now)")
		signal.signal(signal.SIGINT, signal.SIG_DFL)
		self.flag = True


def progress_print(s=None, r=None, lines_up=1, string=None):
	if string:
		tqdm.write("\033[F" * lines_up + "\033[K" + string)
	else:
		tqdm.write(
			"\033[F" * lines_up + f"\033[K{s} sets of {r} timesteps simulated in each world"
		)


c = 0
flag = Flag()
print()
while True:
	for i, world in enumerate(tqdm(worlds, leave=False)):
		# if not c:
		# 	world.drive(50, verbose=2, animate=True, graph=True, nest_tqdm=True)
		# else:
		world.drive(reps, verbose=2, animate=False, graph=False, nest_tqdm=True)
		if i == n_worlds - 1:
			progress_print(c + int(not flag.flag), reps)
			break
	if flag.flag:
		break

	for i, conf in enumerate(configs):
		call(["cp", conf["output"]["data"], "{}/{}.d".format(local_backup, i)])
		call(["cp", conf["output"]["map"], "{}/{}.m".format(local_backup, i)])
		if offsite:
			call("scp -P 2200 {}/{}.* {}/".format(local_backup, i, network_backup), shell=True)

	c += 1
