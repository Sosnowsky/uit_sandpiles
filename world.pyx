# cython: language_level=3
# Set cython to python3 mode

import random
from collections import deque
from itertools import count

import numpy as np
cimport numpy as cnp
import pyqtgraph as pg
from tqdm import tqdm

# More efficient plots
pg.setConfigOptions(antialias=False)


cdef class World:
	cdef:
		# Config options
		int COLS, ROWS
		str INPUT, SAVE, OUTPUT
		float PROB
		bint RUNNING, ZHANG
		float Z_THRESH, Z_EPSILON
		
		# Arrays for containing the plane and the grains to be added between consequtive steps
		cnp.ndarray plane, diff

		# Deques for keeping record of the numbetr of critical spots and total number of grains
		object crits_stat, grains_stat
		
		# Total number of grains
		object grains
	


	def __init__(self, dict config):
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
		self.Z_THRESH = config["z_threshold"]
		self.Z_EPSILON = config["z_epsilon"]


		self.crits_stat = deque(maxlen=600)
		self.grains_stat = deque(maxlen=10000)

		# Initiate the plane (randomly or from file)
		self.init_plane()

		# Initiate grain counter
		self.grains = sum(self.plane.flatten()) + sum(self.diff.flatten())

		# Write header to data file if empty
		with open(self.OUTPUT, "a+") as data_file:
			data_file.seek(0)
			if data_file.readline() == "":
				data_file.seek(0, 2)
				data_file.write(
					f"{self.ROWS} rows, {self.COLS} cols, p={self.PROB:.7f}, running={self.RUNNING}, "
					f"seed={config['seed']}{', zhang' if self.ZHANG else ''}\n"
				)
				data_file.write("critical cells; added grains; lost grains; total grains;\n")
				data_file.write("========================================================\n")

	# Function to initiate plane and diff arrays
	def init_plane(self):
		dtype = float if self.ZHANG else int

		if self.INPUT == "":  # initiate plane randomly
			# Create a function for generating random numbers
			if self.ZHANG:
				def rng(r, c):
					return random.random() * (self.Z_THRESH - 0.5)
			else:
				def rng(r, c):
					return random.randint(0, 3)

			# Initiate plane form said function
			self.plane = self.from_func(dtype, rng)

		else:  # Initiate plane from file
			self.plane = self.from_map(dtype)
		
		# Initiate diff
		self.diff = np.zeros((self.ROWS, self.COLS), dtype=dtype)

	# Parser for map files
	def from_map(self, dtype):
		plane = np.empty((self.ROWS, self.COLS), dtype)
		with open(self.INPUT, "r") as file:
			for y, line in enumerate(file.readlines()):
				plane[y] = np.fromiter(map(dtype, line.rstrip(";\n\r ").split(";")), dtype)
		return plane

	# Convenience function for initiating np array from a function
	def from_func(self, dtype, func):
		v_func = np.vectorize(func)
		plane = np.fromfunction(v_func, (self.ROWS, self.COLS), dtype=dtype)
		return plane

	# Function to drive sandpile to SOC (where the graph of the number of critical spots flattens out)
	def drive_to_stable(self):
		# Deque for keeping track of critical spots in the last 20k timesteps
		q = deque(maxlen=20000)
		# Run model for max_t timesteps or until graph flattens out
		for i in count():
			# Run one timestep and put number of critical points in deque
			if self.ZHANG:
				self.diff = self.z_step()[3]
			else:
				self.diff = self.step()[3]
			q.append(self.grains)

			# Perform analysis every 100 timesteps where the queue is full
			if i % 100 == 0 and len(q) == q.maxlen:
				# Break if the gradient of the regression line is less than a given value (0.01)
				a, b = np.polyfit(range(len(q)), q, 1)
				print("\rStep {}, {:+.5f}".format(i, a), end="")
				if abs(a) < 0.01:
					break
			# Print number of steps run if deque is not full
			elif i % 100 == 0:
				print("\r{}".format(i), end="")

		# Save the stable configuration
		self.save_map()
		print("")

	# Function to drive the sandpile for n steps.
	# Verbosity levels are:
	#   0 - no output
	#   1 - print what timestep is currently running
	#   2 - progress bar
	# If level 2 is used, use 'nest_tqdm=True' if this progress bar is nested within another
	def drive(self, n, verbose=2, animate=False, graph=False, nest_tqdm=False):
		
		if graph or animate:
			# Create window for graphs and/or animation
			pg_win = pg.GraphicsLayoutWidget()
			pg_win.showMaximized()
		if graph:
			# Create widgets for graphs
			c_plot = pg_win.addPlot(row=0, col=0, title="crits")
			t_plot = pg_win.addPlot(row=1, col=0, title="total")
			c_curve = c_plot.plot()
			t_curve = t_plot.plot()
		if animate:
			# Create widget for animation
			canvas = pg_win.addPlot(row=0, col=int(graph), rowspan=2, colspan=2, title="map")
			canvas.setAspectLocked()
			im_item = pg.ImageItem()
			canvas.addItem(im_item)
			

		rng = range(n)
		if verbose == 2:
			# Create progress bar
			rng = tqdm(rng, leave=not nest_tqdm, position=1 if nest_tqdm else None)

		with open(self.OUTPUT, "a+") as data_file:
			for i in rng:
				# Run one timestep
				if self.ZHANG:
					crits, added, lost, self.diff = self.z_step()
				else:
					crits, added, lost, self.diff = self.step()

				# Write data to file
				data_file.write(f"{crits};{added};{lost};{self.grains};\n")

				self.crits_stat.append(crits)
				if graph:
					# Add new stats and update graph
					self.update_stats(animate, crits, c_curve, t_curve, i)

				if verbose == 1:
					# Print progress
					self.verbosity_1(i, n)

				if animate:
					# Show new frame of animation
					self.show_frame(im_item)
					im_item.save(f'media/{i}.png')


		self.save_map()
		if graph or animate:
			pg_win.close()
			pg.QtGui.QApplication.processEvents()

	# Runs one timestep for non-zhang
	cdef step(self):
		# Type declarations for cython
		cdef:
			int lost = 0
			int crits = 0
			int added = 0
			int r, c

			# Bool that tells wether there is anything in the deque
			bint queue_content = bool(self.crits_stat)

			# Array to keep track of topples
			cnp.ndarray[cnp.int_t, ndim=2] new_diff = np.zeros((self.ROWS, self.COLS), dtype=int)

		# If nothing is critical or the sandpile is defined to be running, place new grains
		# This relies on there being content in the crits_stat deque
		if (queue_content and self.crits_stat[-1] == 0) or self.RUNNING:
			added = self.grains_to_add()
			self.grains += added
			for i in range(added):
				r, c = self.rand_pos()
				self.diff[r][c] += 1
		
		# Iterate through all cells on plane
		for r in range(self.ROWS):
			for c in range(self.COLS):
				# If self.diff has content
				if queue_content or self.RUNNING:
					# Skip if nothing to add
					if self.diff[r][c] == 0:
						continue
					# Add non-empty cell of self.diff to self.plane
					self.plane[r][c] += self.diff[r][c]

				# If cell is critical
				if self.plane[r][c] >= 4:
					crits += 1
					new_diff[r][c] -= 4
					# Remove 4 grains from critcal cell and distribute them among adjacent cells
					lost += (
						self.put(new_diff, r - 1, c)
						+ self.put(new_diff, r + 1, c)
						+ self.put(new_diff, r, c - 1)
						+ self.put(new_diff, r, c + 1)
					)

		return crits, added, lost, new_diff

	# Runs one timestep in zhang mode
	cdef z_step(self):
		# Type declarations for cython
		cdef:
			float lost = 0
			int crits = 0
			int added = 0
			int r, c

			# Bool that tells wether there is anything in the deque
			bint queue_content = bool(self.crits_stat)

			# Empty array to keep track of topples
			cnp.ndarray[cnp.float_t, ndim=2] new_diff = np.zeros((self.ROWS, self.COLS), dtype=float)

		# If nothing is critical or the sandpile is defined to be running, place new grains
		# This relies on there being content in the crits_stat deque
		if (queue_content and self.crits_stat[-1] == 0) or self.RUNNING:
			added = self.grains_to_add()
			self.grains += added
			for i in range(added):
				r, c = self.rand_pos()
				self.diff[r][c] += 1

		# Iterate through all cells on plane
		for r in range(self.ROWS):
			for c in range(self.COLS):
				# If self.diff has content
				if queue_content or self.RUNNING:
					# Skip if nothing to add
					if self.diff[r][c] == 0:
						continue
					# Add non-empty cell of self.diff to self.plane
					self.plane[r][c] += self.diff[r][c]

				# If cell is critical
				if self.plane[r][c] >= self.Z_THRESH:
					crits += 1
					new_diff[r][c] -= (1 - self.Z_EPSILON) * self.plane[r][c]
					# Remove grains from critcal cell and distribute them among adjacent cells
					to_add = (1 - self.Z_EPSILON) * self.plane[r][c] / 4

					lost += (
						self.z_put(new_diff, r - 1, c, to_add)
						+ self.z_put(new_diff, r + 1, c, to_add)
						+ self.z_put(new_diff, r, c - 1, to_add)
						+ self.z_put(new_diff, r, c + 1, to_add)
					)

		return crits, added, lost, new_diff

	# Returns number of grains to add
	cdef grains_to_add(self):
		# return np.random.binomial(self.ROWS * self.COLS, self.PROB)
		return 1

	# Returns random position to place new grain on (r, c)
	cdef rand_pos(self):
		cdef:
			int r, c
		r = random.randint(0, self.ROWS - 1)
		c = random.randint(0, self.COLS - 1)
		return r, c

	# Function to place grains on non-zhang plane
	cdef put(self, cnp.ndarray[cnp.int_t, ndim=2] diff, int r, int c):
		# Type definitions for cython
		cdef:
			tuple coords
			int lost

		# If coords are outside of plane
		if r == -1 or r == self.ROWS or c == -1 or c == self.COLS:
			# Find out what to do with grains
			coords = self.bound(r, c)
			if coords is not None:
				diff[coords[0]][coords[1]] += 1
			else:
				lost = 1
				self.grains -= 1
		else:
			diff[r][c] += 1
			lost = 0
		return lost

	# Function to place grains on zhang plane
	cdef z_put(self, cnp.ndarray[cnp.float_t, ndim=2] diff, int r, int c, float to_add):
		# Type definitions for cython
		cdef:
			tuple coords
			float lost
			
		# If coords are outside of plane
		if r == -1 or r == self.ROWS or c == -1 or c == self.COLS:
			# Find out what to do with grains
			coords = self.bound(r, c)
			if coords is not None:
				diff[coords[0]][coords[1]] += to_add
			else:
				lost = to_add
				self.grains -= to_add
		else:
			diff[r][c] += to_add
			lost = 0
		return lost

	cdef bound(self, r, c):
		# BOUNDARY CONDITION - if grain is lost, return None. Otherwise, return position to place grain as tuple (r, c)
		return None

	# Function to update graphs and optional stat-deque
	# (The 'self.grains_stat' is not needed for anything other than graphing)
	def update_stats(self, animate, crits, c_curve, t_curve, step):
		self.grains_stat.append(self.grains)
		# Only update graphs every 50 steps unless animation is enabled
		if step % 50 == 0 or animate:
			c_curve.setData(self.crits_stat)
			t_curve.setData(self.grains_stat)
			if not animate: # If animation is enabled, 'show_frame()' will update screen
				pg.QtGui.QApplication.processEvents()

	# Print progress for verbosity level 1
	def verbosity_1(self, step, tot):
		print("\r{}/{}".format(step + 1, tot), end="")
		if step == tot - 1:
			print("")

	# Function to show frame in animation
	def show_frame(self, im_item):
		im_item.setImage(self.plane, autoLevels=False, levels=(0, 4))
		pg.QtGui.QApplication.processEvents()

	# Function to save current plane to file
	def save_map(self):
		if self.SAVE != "":
			with open(self.SAVE, "w+") as save_file:
				for line in self.draw():
					save_file.write(line+'\n')

	# Returns a generator of strings - each string contains a row of the plane
	def draw(self):
		return (';'.join(map(str, cells)) for cells in self.plane)

