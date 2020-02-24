import random
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation


class World:

	def __init__(self, config):
		random.seed(config['seed'])

		self.CRIT = config['criticality']
		self.COLS = config['columns']
		self.ROWS = config['rows']
		self.INPUT = config['input']
		self.SAVE = config['output']['map']
		self.OUTPUT = config['output']['data']

		self.t = 0
		self.topples = 0
		self.flux = 0

		self.init_plane()  # Initiate the plane randomly or from file
		self.reset_animation()

		# Write header to data file
		with open(self.OUTPUT, 'a+') as data_file:
			data_file.write(
				'========================================================\n')
			data_file.write(
				't; topples; grains; flux; last insertion;\n')

	def init_plane(self):
		if self.INPUT == '':  # initiate plane randomly
			self.plane = np.fromfunction(np.vectorize(lambda r, c: random.randint(
				0, self.CRIT - 1)), (self.ROWS, self.COLS), dtype=int)
		else:  # Initiate plane from file
			self.plane = np.empty((self.ROWS, self.COLS), dtype=int)
			with open(self.INPUT, 'r') as file:
				for y, line in enumerate(file.readlines()):
					self.plane[y] = np.array(list(map(int, line.rstrip(';\n\r ').split(';'))))

			# Make sure the plane is stable before beginning
			for r in range(self.plane.shape[0]):
				for c in range(self.plane.shape[1]):
					self.put(r, c, n=0, placed=False)

		# Calculate the number of grains
		self.grains = sum(self.plane.flatten())

	def step(self, animate=False):
		self.topples = 0  # cumulative?
		self.flux = 0   # cumulative?

		# Place a grain in a random cell
		self.put(random.randint(0, self.ROWS - 1),
		         random.randint(0, self.COLS - 1), animate=animate)

	# Modifiable boundary condition
	def boundary(self, r, c):
		self.void(r, c)

	def void(self, r, c):
		self.flux += 1
		self.grains -= 1

	def rollover(self, r, c):
		self.put(r % self.ROWS, c % self.COLS, placed=False)

	def rollover_y(self, r, c):
		if r == -1 or r == self.ROWS:
			self.flux += 1
			self.grains -= 1
		else:
			self.put(r, c % self.COLS, placed=False)

	# Place n grains in a cell and recursively calculate the consequences
	def put(self, r, c, n=1, placed=True, animate=False):

		# Call boundary func if the indecies exceed the world plane
		if r == -1 or r == self.ROWS or c == -1 or c == self.COLS:
			self.boundary(r, c)
		else:
			if animate:
				tmp = self.plane[r][c]
				self.plane[r][c] = 20
				self.add_frame()
				self.plane[r][c] = tmp
			if placed:  # If the function was called at the beginning of a timestep
				self.grains += n
				self.lr = r
				self.lc = c
				self.t += 1

			self.plane[r][c] += n  # Add n grains
			while self.plane[r][c] >= self.CRIT:  # While pile height is critical
				# Topple, placing grains in each adjacent csll
				self.topples += 1
				self.plane[r][c] -= self.CRIT

				for i in range(self.CRIT):
					mod = i % self.CRIT
					if mod == 0:
						self.put(r + 1, c, placed=False, animate=animate)
					elif mod == 1:
						self.put(r, c + 1, placed=False, animate=animate)
					elif mod == 2:
						self.put(r - 1, c, placed=False, animate=animate)
					elif mod == 3:
						self.put(r, c - 1, placed=False, animate=animate)

	# Runs the simulation for n timesteps, optionally printing the world
	# plane and info at each timestep. Also saves data and map.
	def drive(self, n, verbose=1, animate=False):
		with open(self.OUTPUT, 'a+') as data_file:
			for i in range(n):
				self.step(animate=animate)
				data_file.write(self.info() + '\n')
				if verbose == 1:
					print('\r{}/{}'.format(i, n), end='')
				if verbose == 2:
					print(self.draw() + self.info())

		if self.SAVE != '':
			with open(self.SAVE, 'w+') as save_file:
				save_file.write(self.draw())

		if animate:
			self.show_animation()

	# Returns info about the last timestep
	def info(self):
		s = '{}; {}; {}; {}; [{}, {}];'.format(
			self.t, self.topples, self.grains, self.flux, self.lr, self.lc)
		return s

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
			self.frames[0], animated=True, cmap='jet', vmax=20, vmin=0)

		ani = animation.FuncAnimation(self.canvas, self.get_frame, frames=range(
			len(self.frames)), interval=50, blit=True, repeat=True, repeat_delay=1000)
		plt.show()
		self.reset_animation()

	def get_frame(self, i):
		self.im.set_array(self.frames[i])
		return self.im,

	def add_frame(self):
		self.frames.append(np.copy(self.plane))
