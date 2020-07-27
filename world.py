import random
from collections import deque

import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np
import pyqtgraph as pg
from tqdm import tqdm

pg.setConfigOptions(antialias=False)


class World:
	def __init__(self, config):
		random.seed(config["seed"])
		np.random.seed(config["seed"])

		self.COLS = config["columns"]
		self.ROWS = config["rows"]
		self.INPUT = config["input"]
		self.PROB = config["probability"]
		self.RUNNING = config["running"]
		self.SAVE = config["output"]["map"]
		self.OUTPUT = config["output"]["data"]
		self.ZHANG = config["zhang"]
		self.Z_EPSILON = config["z_epsilon"]

		if self.ZHANG:
			self.DTYPE = float
			self.C_THRESH = config["z_threshold"]
		else:
			self.DTYPE = int
			self.C_THRESH = 4

		self.grains = 0
		self.plane = None
		# Array to keep track of topples between function calls
		self.persistent_diff = np.zeros((self.ROWS, self.COLS), dtype=self.DTYPE)

		self.stats = {"crits": deque(maxlen=600), "grains": deque(maxlen=10000)}

		self.init_plane()  # Initiate the plane (randomly or from file)

		# Write header to data file (unless we're reading an input map)
		if self.INPUT == "":
			with open(self.OUTPUT, "a+") as data_file:
				data_file.write(
					"{} rows, {} cols, p={}, running={}, seed={}\n".format(
						self.ROWS, self.COLS, self.PROB, self.RUNNING, config["seed"]
					)
				)
				data_file.write("critical cells; added grains; lost grains; total grains;\n")
				data_file.write("========================================================\n")

	def init_plane(self):
		if self.INPUT == "":  # initiate plane randomly
			if self.ZHANG:
				rng = np.vectorize(lambda r, c: random.random() * (self.Z_THRESH - 0.5))
			else:
				rng = np.vectorize(lambda r, c: random.randint(0, 3))
			self.plane = np.fromfunction(rng, (self.ROWS, self.COLS), dtype=self.DTYPE)
		else:  # Initiate plane from file
			self.plane = np.empty((self.ROWS, self.COLS), dtype=self.DTYPE)
			with open(self.INPUT, "r") as file:
				for y, line in enumerate(file.readlines()):
					self.plane[y] = np.array(list(map(self.DTYPE, line.rstrip(";\n\r ").split(";"))))

			self.persistent_diff = self.step(None, 1)[3]
		# Calculate the number of grains
		self.grains = sum(self.plane.flatten()) + sum(self.persistent_diff.flatten())

	# Runs one timestep
	def step(self, p_diff, p_crits):

		lost = 0
		added = 0
		# Create empty array to keep track of topples
		diff = np.zeros((self.ROWS, self.COLS), dtype=self.DTYPE)
		# If nothing is critical or the sandpile is defined to be running, place new grains
		if p_crits == 0 or self.RUNNING:
			added = self.grains_to_add()
			for i in range(added):
				r_, c_ = self.rand_pos()
				p_diff[r_][c_] += 1
		crits = 0
		self.grains += added

		# Function to place grain on adjacent cells
		def put(r, c, to_add):
			nonlocal lost
			try:
				diff[r][c] += to_add
			except IndexError:
				coords = self.bound(r, c)
				if coords:
					diff[coords[0]][coords[1]] += to_add
				else:
					lost += to_add
					self.grains -= to_add

		for r in range(self.ROWS):
			for c in range(self.COLS):
				if type(p_diff) != type(None):
					if p_diff[r][c] == 0:
						continue

					self.plane[r][c] += p_diff[r][c]
				if self.plane[r][c] >= self.C_THRESH:
					crits += 1
					if self.ZHANG:
						diff[r][c] -= (1 - self.Z_EPSILON) * self.plane[r][c]
					else:
						diff[r][c] -= 4

					if self.ZHANG:
						to_add = (1 - self.Z_EPSILON) * self.plane[r][c] / 4
					else:
						to_add = 1
					put(r - 1, c, to_add)
					put(r + 1, c, to_add)
					put(r, c - 1, to_add)
					put(r, c + 1, to_add)

		return crits, added, lost, diff

	def bound(self, r, c):
		# BOUNDARY CONDITION - if grain is lost, return None. Otherwise, return position to place grain as tuple (r, c)
		return None

	# Returns random position to place new grain on (r, c)
	def rand_pos(self):
		r = random.randint(0, self.ROWS - 1)
		c = random.randint(0, self.COLS - 1)
		return r, c

	# Returns number of grains to add
	def grains_to_add(self):
		return np.random.binomial(self.ROWS * self.COLS, self.PROB)

	# Function to drive sandpile to SOC (where the graph oh the number of crits flattens out)
	def drive_to_stable(self, max_t=1000000000):
		q = deque(maxlen=20000)
		diff = self.persistent_diff
		crits = 0
		# Run model for max_t timesteps or until graph flattens out
		for i in range(max_t):
			crits, added, lost, diff = self.step(diff, crits)
			q.append(self.grains)
			# Every 100 timesteps where the queue is full
			if len(q) == q.maxlen and i % 100 == 0:
				# Break if the gradient of the regression line is less than a given value
				a, b = np.polyfit(range(len(q)), q, 1)
				print("\rStep {}, {:+.5f}".format(i + 1, a), end="")
				if abs(a) < 0.01:
					break
			elif i % 100 == 0:
				print("\r{}".format(i + 1), end="")

		print("")
		self.persistent_diff = diff

	# Runs the simulation for n timesteps and saves data
	def drive(self, n, verbose=2, animate=False, graph=False):
		if animate:
			self.reset_animation()
		# Create graphs
		if graph:
			pg_win = pg.GraphicsWindow()
			c_plot = pg_win.addPlot(row=0, col=0, title="crits")
			t_plot = pg_win.addPlot(row=1, col=0, title="total")
			c_curve = c_plot.plot()
			t_curve = t_plot.plot()

		diff = self.persistent_diff
		crits = 0

		rng = range(n)
		# Create loading bar
		if verbose == 2:
			rng = tqdm(rng)

		with open(self.OUTPUT, "a+") as data_file:
			for i in rng:
				# Run one timestep and save data
				crits, added, lost, diff = self.step(diff, crits)
				data_file.write("{};{};{};{};\n".format(crits, added, lost, self.grains))

				if animate:
					self.add_frame()

				# Print progress and optionally map
				if verbose == 1:
					print("\r{}/{}".format(i + 1, n), end="")
					if i == n - 1:
						print("")
				elif verbose == 3:
					print(self.draw() + "\n")

				if graph:
					self.stats["crits"].append(crits)
					self.stats["grains"].append(self.grains)
					if i % 50 == 0:
						c_curve.setData(self.stats["crits"])
						t_curve.setData(self.stats["grains"])
						pg.QtGui.QApplication.processEvents()

		self.persistent_diff = diff

		if self.SAVE != "":
			with open(self.SAVE, "w+") as save_file:
				save_file.write(self.draw())
		if animate:
			self.show_animation()
		if graph:
			pg_win.close()

	# Returns a map of the world plane
	def draw(self):
		s = ""
		for r in self.plane:
			for cell in r:
				s += "{};".format(cell)
			s += "\n"

		return s

	def reset_animation(self):
		self.frames = []
		self.canvas = plt.figure()

	def show_animation(self):
		self.im = plt.imshow(self.frames[0], animated=True, cmap="jet", vmax=5, vmin=0)

		ani = animation.FuncAnimation(
			self.canvas,
			self.get_frame,
			frames=range(len(self.frames)),
			interval=10,
			blit=True,
			repeat=True,
			repeat_delay=1000,
		)
		# ani.save('data/out_ani.mp4', bitrate=30000)   # uncomment this to save animation
		plt.show()
		self.reset_animation()

	def get_frame(self, i):
		self.im.set_array(self.frames[i])
		return (self.im,)

	def add_frame(self):
		self.frames.append(np.copy(self.plane))


if __name__ == "__main__":
	from yaml import safe_load

	config = dict()
	with open("config.yml", "r") as cfg:
		config = safe_load(cfg)
	world = World(config)
	world.drive(1000, 2, 1, 1)
