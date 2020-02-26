import random
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from tqdm import tqdm


class World:

	def __init__(self, config):
		random.seed(config['seed'])
		np.random.seed(config['seed'])

		self.COLS = config['columns']
		self.ROWS = config['rows']
		self.INPUT = config['input']
		self.PROB = config['probability']
		self.RUNNING = config['running']
		self.SAVE = config['output']['map']
		self.OUTPUT = config['output']['data']

		self.grains = 0
		self.plane = np.array(None)
		self.persistent_diff = np.zeros((self.ROWS, self.COLS), dtype=int)

		self.stats = {
			'crits': [],
			'lost': [],
			'grains': []
		}

		self.init_plane()  # Initiate the plane randomly or from file

		# Write header to data file
		with open(self.OUTPUT, 'a+') as data_file:
			data_file.write(
                            '========================================================\n')
			data_file.write(
                            'critical cells; added grains; lost grains; total grains;\n')
			data_file.write(
                            '========================================================\n')

	def init_plane(self):
		if self.INPUT == '' or self.INPUT == 'OVERCRITICAL':  # initiate plane randomly
			self.plane = np.fromfunction(np.vectorize(lambda r, c: random.randint(
                            0, 3)), (self.ROWS, self.COLS), dtype=int)
			if self.INPUT == 'OVERCRITICAL':
				self.persistent_diff = np.full((self.ROWS, self.COLS), 4)
		else:  # Initiate plane from file
			self.plane = np.empty((self.ROWS, self.COLS), dtype=int)
			with open(self.INPUT, 'r') as file:
				for y, line in enumerate(file.readlines()):
					self.plane[y] = np.array(list(map(int, line.rstrip(';\n\r ').split(';'))))

		# Calculate the number of grains
		self.grains = sum(self.plane.flatten())

	# Runs one timestep
	def step(self, p_diff, p_crits):

		lost = 0
		added = 0
		diff = np.zeros((self.ROWS, self.COLS), dtype=int)
		if p_crits == 0 or self.RUNNING:
			added = np.random.binomial(self.ROWS * self.COLS, self.PROB)
			for i in range(added):
				r_, c_ = self.rand_pos()
				p_diff[r_][c_] += 1
		crits = 0
		self.grains += added

		# Function to place grain on adjacent cells
		def put(r, c):
			nonlocal lost
			try:
				diff[r][c] += 1
			except IndexError:
				coords = self.bound(r, c)
				if coords:
					diff[coords[0]][coords[1]] += 1
				else:
					lost += 1
					self.grains -= 1

		for r in range(self.ROWS):
			for c in range(self.COLS):
				if p_diff[r][c] == 0:
					continue

				self.plane[r][c] += p_diff[r][c]
				if self.plane[r][c] >= 4:
					crits += 1
					diff[r][c] -= 4
					put(r - 1, c)
					put(r + 1, c)
					put(r, c - 1)
					put(r, c + 1)

		return crits, added, lost, diff

	def bound(self, r, c):
		# BOUNDARY CONDITION - if grain is lost, return None. Otherwise, return position to place grain as tuple
		return None
		# /BOUNDARY CONDITION

	# Returns random position to place new grain on
	def rand_pos(self):
		r = random.randint(0, self.ROWS - 1)
		c = random.randint(0, self.COLS - 1)
		return r, c

	# Runs the simulation for n timesteps and saves data
	def drive(self, n, verbose=1, animate=False):
		if animate:
			self.reset_animation()
		with open(self.OUTPUT, 'a+') as data_file:
			diff = self.persistent_diff
			crits = 0
			rng = range(n)
			if verbose == 2:
				rng = tqdm(rng, ncols=100)

			for i in rng:
				crits, added, lost, diff = self.step(diff, crits)
				data_file.write('{};{};{};{};\n'.format(crits, added, lost, self.grains))
				self.stats['crits'].append(crits)
				self.stats['lost'].append(lost)
				self.stats['grains'].append(self.grains)
				if animate:
					self.add_frame()
				if verbose == 1:
					print('\r{}/{}'.format(i + 1, n), end='')
					if i == n - 1:
						print('')
				elif verbose == 3:
					print(self.draw() + '\n')
			self.persistent_diff = diff

		if self.SAVE != '':
			with open(self.SAVE, 'w+') as save_file:
				save_file.write(self.draw())
		if animate:
			self.show_animation()
		else:
			plt.plot(self.stats['crits'])
			plt.plot(self.stats['lost'])
			plt.plot(self.stats['grains'])
			plt.show()

	# Returns a map of the world plane
	def draw(self):
		s = ''
		for r in self.plane:
			for cell in r:
				s += '{};'.format(cell)
			s += '\n'

		return s

	def reset_animation(self):
		self.frames = []
		self.canvas = plt.figure()

	def show_animation(self):
		self.im = plt.imshow(
                    self.frames[0], animated=True, cmap='jet', vmax=5, vmin=0)

		ani = animation.FuncAnimation(self.canvas, self.get_frame, frames=range(
                    len(self.frames)), interval=10, blit=True, repeat=True, repeat_delay=1000)
		# ani.save('data/out_ani.mp4', bitrate=30000)   # uncomment this to save animation
		plt.show()
		self.reset_animation()

	def get_frame(self, i):
		self.im.set_array(self.frames[i])
		return self.im,

	def add_frame(self):
		self.frames.append(np.copy(self.plane))
