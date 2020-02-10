import random
import numpy as np


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

		self.init_plane()

		with open(self.OUTPUT, 'a+') as data_file:
			data_file.write(
				'========================================================\n')
			data_file.write(
				't; topples; grains; flux; last insertion;\n')

	def init_plane(self):
		if self.INPUT == '':
			self.plane = np.fromfunction(np.vectorize(lambda r, c: random.randint(
				0, self.CRIT - 1)), (self.ROWS, self.COLS), dtype=int)
		else:
			self.plane = np.empty((self.ROWS, self.COLS), dtype=int)
			with open(self.INPUT, 'r') as file:
				for y, line in enumerate(file.readlines()):
					self.plane[y] = np.array(list(map(int, line.rstrip(';\n\r ').split(';'))))

			for r in range(self.plane.shape[0]):
				for c in range(self.plane.shape[1]):
					self.put(r, c, n=0, placed=False)

		self.grains = sum(self.plane.flatten())

	def step(self):
		self.topples = 0  # cumulative?
		self.flux = 0   # cumulative?

		self.put(random.randint(0, self.ROWS - 1),
		         random.randint(0, self.COLS - 1))

	def boundary(self, r, c):
		self.flux += 1
		self.grains -= 1

	def put(self, r, c, n=1, placed=True):
		if r == -1 or r == self.ROWS or c == -1 or c == self.COLS:
			self.boundary(r, c)
		else:
			if placed:
				self.grains += n
				self.lr = r
				self.lc = c
				self.t += 1

			self.plane[r][c] += n
			while self.plane[r][c] >= self.CRIT:
				self.topples += 1

				self.plane[r][c] -= self.CRIT

				self.put(r + 1, c, placed=False)
				self.put(r - 1, c, placed=False)
				self.put(r, c + 1, placed=False)
				self.put(r, c - 1, placed=False)

	def info(self):
		s = '{}; {}; {}; {}; [{}, {}];'.format(
			self.t, self.topples, self.grains, self.flux, self.lr, self.lc)
		return s

	def draw(self):
		s = ''
		for r in self.plane:
			for cell in r:
				s += '{};'.format(cell)
			s += '\n'

		return s

	def drive(self, n, verbose=False):
		with open(self.OUTPUT, 'a+') as data_file:
			for i in range(n):
				self.step()
				data_file.write(self.info() + '\n')
				if verbose:
					print(self.draw() + self.info() + '\n')

		if self.SAVE != '':
			with open(self.SAVE, 'w+') as save_file:
				save_file.write(self.draw())
