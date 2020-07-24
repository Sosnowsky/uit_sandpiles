from yaml import safe_load
from world import World
from subprocess import call
import signal

local_backup = "backups"
network_backup = "rasmus@bringebaerpai.duckdns.org:~/backups"

config = dict()
with open("config.yml", "r") as cfg:
	config = safe_load(cfg)

call(["cp", "config.yml", local_backup + "/"])
call(["scp", "-P", "2200", "config.yml", network_backup + "/"])

world = World(config)


if config["input"] == "":
	print(
		"No input file specified - initiating randomly and driving to a critical configuration"
	)
	world.drive_to_stable()


class Flag:
	def __init__(self):
		self.flag = False
		signal.signal(signal.SIGINT, self.change_state)

	def change_state(self, signum, frame):
		print("Exit flag set to True (repeat to exit now)")
		signal.signal(signal.SIGINT, signal.SIG_DFL)
		self.flag = True


c = 0
flag = Flag()
while True:
	for i in range(100):
		world.drive(100, verbose=2, animate=False, graph=False)
		if flag.flag:
			print("Exiting")
			break

	print("Creating backup")
	call(["cp", config["output"]["data"], "{}/{}.d".format(local_backup, c % 10)])
	call(["cp", config["output"]["map"], "{}/{}.m".format(local_backup, c % 10)])
	call(
		"scp -P 2200 {}/{}.* {}/".format(local_backup, c % 10, network_backup), shell=True
	)
	if flag.flag:
		break

	c += 1
