import random
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation


class World:

	def __init__(self, config):
		random.seed(config['seed'])

		self.COLS = config['columns']
		self.ROWS = config['rows']
		self.INPUT = config['input']
		self.SAVE = config['output']['map']
		self.OUTPUT = config['output']['data']

		self.grains = 0
		self.plane = np.array()

		self.init_plane()  # Initiate the plane randomly or from file

		# Write header to data file
		with open(self.OUTPUT, 'a+') as data_file:
			data_file.write(
				'=========================================\n')
			data_file.write(
				't; topples; grains; flux; last insertion;\n')
			data_file.write(
				'=========================================\n')

	def init_plane(self):
		if self.INPUT == '':  # initiate plane randomly
			self.plane = np.fromfunction(np.vectorize(lambda r, c: random.randint(
				0, 3)), (self.ROWS, self.COLS), dtype=int)

		else:  # Initiate plane from file
			self.plane = np.empty((self.ROWS, self.COLS), dtype=int)
			with open(self.INPUT, 'r') as file:
				for y, line in enumerate(file.readlines()):
					self.plane[y] = np.array(list(map(int, line.rstrip(';\n\r ').split(';'))))

		# Calculate the number of grains
		self.grains = sum(self.plane.flatten())

	def step(self, p_diff, p_crits):
		lost = 0
		diff = np.zeros((self.ROWS, self.COLS), dtype=int)
		if crits == 0 or self.running:
			pass  # Add new grains- binomial stuff
		else:
			added = 0
		crits = 0

		for r in range(len(self.plane)):
			for c in range(len(r)):
				if p_diff[r][c] == 0:
					continue

				self.plane[r][c] += p_diff[r][c]
				if self.plane[r][c] >= 4:
					crits += 1
					diff -= 4
					try:
						diff[r - 1][c] += 1
					except IndexError:
						coords = self.bound(r - 1, c)
						if coords:
							diff[coords[0]][coords[1]] += 1
						else:
							lost += 1
					try:
						diff[r + 1][c] += 1
					except IndexError:
						coords = self.bound(r + 1, c)
						if coords:
							diff[coords[0]][coords[1]] += 1
						else:
							lost += 1
					try:
						diff[r][c - 1] += 1
					except IndexError:
						coords = self.bound(r, c - 1)
						if coords:
							diff[coords[0]][coords[1]] += 1
						else:
							lost += 1
					try:
						diff[r][c + 1] += 1
					except IndexError:
						coords = self.bound(r, c + 1)
						if coords:
							diff[coords[0]][coords[1]] += 1
						else:
							lost += 1

		return crits, added, lost, diff

	def bound(self, r, c):
		# BOUNDARY CONDITION - if grain is lost, return None. Otherwise, return position to place grain
		return None
		# /BOUNDARY CONDITION

	# Runs the simulation for n timesteps and saves data
	def drive(self, n, verbose=1, animate=False):
		with open(self.OUTPUT, 'a+') as data_file:
			diff = np.zeros((self.ROWS, self.COLS), dtype=int)
			crits = 0
			for i in range(n):
				crits, added, lost, diff = self.step(diff, crits)
				data_file.write('{};{};{};{};\n'.format(crits, added, lost, self.grains))
				if verbose == 1:
					print('\r{}/{}'.format(i, n), end='')
				elif verbose == 2:
					print(self.draw() + '\n')
			if verbose == 1:
				print('\r{}/{}'.format(n, n))

		if self.SAVE != '':
			with open(self.SAVE, 'w+') as save_file:
				save_file.write(self.draw())

	# Returns a map of the world plane
	def draw(self):
		s = ''
		for r in self.plane:
			for cell in r:
				s += '{};'.format(cell)
			s += '\n'

		return s
