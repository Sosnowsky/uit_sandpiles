import numpy as np
import pyqtgraph as pg
from pyqtgraph import QtGui, QtCore
from tqdm import tqdm
from more_itertools import pairwise
from time import sleep
from definitions import n_thresholds

datadir = "prange_5e-6"


class Button(QtGui.QGraphicsProxyWidget):
	# Wrapper class for pyqtgraph button

	sigPressed = QtCore.Signal(object)

	def __init__(self, text):
		QtGui.QGraphicsProxyWidget.__init__(self)
		self.btn = QtGui.QPushButton(text)
		self.btn.clicked.connect(lambda x: self.sigPressed.emit(x))
		self.btn.setStyleSheet(
			"QPushButton { background-color: white }"
			"QPushButton:pressed { background-color: lightblue }"
		)
		self.setWidget(self.btn)

	def setText(self, text):
		self.btn.setText(text)


class LinearRegionPlot(pg.PlotItem):
	# Class combining a plotItem with a linearRegionItem
	# Also supplies some convenience class for plotting

	def __init__(self, symbolSize, onChange=None, *args, **kwargs):
		# Variables to store plot data
		self.x = None
		self.y = None

		self.symbolSize = symbolSize

		# Variable to store coefficient from regression
		self.coeff = None

		# By default call self.loglog_plot when region is changed
		if onChange is None:
			onChange = self.loglog_plot
		pg.PlotItem.__init__(self, *args, **kwargs)
		self.region = pg.LinearRegionItem()
		self.addItem(self.region)
		self.region.sigRegionChangeFinished.connect(onChange)
		self.disableAutoRange()

	def clear(self):
		# CLear plot, but keep region
		pg.PlotItem.clear(self)
		self.addItem(self.region)

	def getRegion(self):
		return self.region.getRegion()

	def loglog_plot(self, x=None, y=None):
		# Function to:
		#  Create or update scatterplot
		#  Highlight points within region
		#  Perform regression on said points and plot regression line
		self.clear()

		# If y is None, we simply update the plot with our current values
		if y is not None:
			self.x, self.y = loglog(x, y)

		l_lim, u_lim = self.getRegion()
		mask = (self.x > l_lim) & (self.x < u_lim)
		val_x = self.x[mask]

		val_y = self.y[mask]
		inval_x = self.x[~mask]
		inval_y = self.y[~mask]

		self.plot(
			val_x,
			val_y,
			symbolSize=self.symbolSize,
			symbol="o",
			symbolPen=None,
			symbolBrush="g",
			pen=None,
		)

		self.plot(
			inval_x,
			inval_y,
			symbolSize=self.symbolSize,
			symbol="o",
			symbolPen=None,
			symbolBrush="r",
			pen=None,
		)

		self.autoRange()

		# Perform regression
		try:
			line = np.polyfit(val_x, val_y, 1)
			self.coeff = line[0]
			self.line_on_plot(line)
		except:
			pass

	def line_on_plot(self, line, pen="b", name=None):
		# Function to plot a line - This could probably be replaced by some pyqtgraph builtin
		a, b = line
		xs = self.getAxis("bottom").range
		ys = list(map(lambda x: a * x + b, xs))
		self.plot(xs, ys, pen=pen, name=name)


def loglog(x, y):
	# Log-transform two series
	x = np.array(x)
	y = np.array(y)
	mask = (x != 0) & (y != 0)
	return np.log10(x[mask]), np.log10(y[mask])


def pdf(x, bins):
	# Create a probability density function
	# I'm not sure whether this is a valid pdf (I dont think its definite integral is 1) when using log-bins, as in this file
	pdf, edges = np.histogram(x, bins=bins, density=True)
	bins = np.array([(e1 + e2) / 2 for e1, e2 in pairwise(edges)])
	return bins, pdf


def series_from_file(fname, n_series, dtypes):
	# Read and return n_series series from a file
	# dtypes is a list of types
	data = [] if n_series == 1 else [[] for i in range(n_series)]
	with open(fname, "r") as file:
		for line in file.readlines():
			if n_series == 1:
				data.append(dtypes[0](line))
			else:
				split = line.split(";")
				for d, s, t in zip(data, split, dtypes):
					d.append(t(s))
	return data


def categorized_series_from_file(fname, n_series, dtypes, cat_idx, series_idx):
	# Read n_series series from a file and categorize them
	# The file should be semicolon separated
	# Each line should have an int representing the category of this line's data
	# This int is pointed to by cat_idx
	# The actual data should be pointed to by the elements of series_idx
	# This data is casted to the type element of dtypes with the same index

	data = []
	with open(fname, "r") as file:
		for line in file.readlines():
			subs = line.split(";")
			cat = int(subs[cat_idx])

			if cat >= len(data):
				for i in range(cat - len(data) + 1):
					data.append([] if n_series == 1 else [[] for i in range(n_series)])
			if n_series == 1:
				data[cat].append(dtypes[0](subs[series_idx[0]]))
			else:
				for i in range(n_series):
					data[cat][i].append(dtypes[i](subs[series_idx[i]]))
	return data


# Number of trials run with different robabilities
n_files = 20

# Create window for gui
win = pg.GraphicsLayoutWidget()
win.show()

# Create plot for analysing spectral density
crit_freq_plot = LinearRegionPlot(4, title="frequency spectrum of # of crits")

# Lists of coefficients gathered in this program
freq_coeffs = []
q_pdf_coeffs = [[] for i in range(n_thresholds)]
dur_pdf_coeffs = [[] for i in range(n_thresholds)]
a_pdf_coeffs = [[] for i in range(n_thresholds)]
dur_a_coeffs = [[] for i in range(n_thresholds)]

# Index variable pointing to the next data to analyse
counter = 1


def load_freqs(num):
	# Function to load next spectral density data from file
	global density, freq
	freq, density = series_from_file(f"data/{datadir}/{num}.f", 2, dtypes=[float, float])
	crit_freq_plot.loglog_plot(freq, density)


def advance_freqs():
	# Function to store results from analysis of current batch and load next batch
	global counter
	freq_coeffs.append(crit_freq_plot.coeff)
	if counter < n_files:
		load_freqs(counter)
		counter += 1
	else:
		print("Enter to proceed")
		return -1


def lock_and_run_freqs():
	# Function to analyse all batches with current region bounds
	while advance_freqs() != -1:
		pg.QtGui.QApplication.processEvents()
		sleep(0.1)


btn_next = Button("next")
btn_run = Button("lock and finish")
btn_next.sigPressed.connect(advance_freqs)
btn_run.sigPressed.connect(lock_and_run_freqs)

win.addItem(crit_freq_plot, row=0, col=0)
win.addItem(btn_next, row=1, col=0)
win.addItem(btn_run, row=2, col=0)
win.showMaximized()

load_freqs(0)

# When input is received, we proceed to analysis of thresholded data
# Yes, this is very hacky - should probably be replaced with some QApp.exec() or something
input()


def lock_and_run_file():
	# Analyse all batches with current threshold using current boundaries
	while advance() not in (1, -1):
		pg.QtGui.QApplication.processEvents()


def lock_and_run_all():
	# Analyse ALL batches using current boundaries
	while advance() != -1:
		pg.QtGui.QApplication.processEvents()


def advance():
	# Store results from analysis of current batch and proceed to next
	global counter
	t = (counter - 1) // n_files
	q_pdf_coeffs[t].append(q_pdf_plot.coeff)
	dur_pdf_coeffs[t].append(dur_pdf_plot.coeff)
	a_pdf_coeffs[t].append(a_pdf_plot.coeff)
	dur_a_coeffs[t].append(dur_a_plot.coeff)
	if counter < n_files * n_thresholds:
		load_plots(counter)
	else:
		save_coeffs()
		return -1
	counter += 1
	if (counter - 1) % n_files == 0:
		return 1


def save_coeffs():
	# Save all coefficients to files
	print("saving")
	with open(f"data/{datadir}/freq.c", "w") as file:
		for i in freq_coeffs:
			file.write(str(i) + "\n")
	with open(f"data/{datadir}/q_pdf.c", "w") as file:
		for i in q_pdf_coeffs:
			file.write(";".join(map(str, i)) + "\n")
	with open(f"data/{datadir}/dur_pdf.c", "w") as file:
		for i in dur_pdf_coeffs:
			file.write(";".join(map(str, i)) + "\n")
	with open(f"data/{datadir}/a_pdf.c", "w") as file:
		for i in a_pdf_coeffs:
			file.write(";".join(map(str, i)) + "\n")
	with open(f"data/{datadir}/dur_a.c", "w") as file:
		for i in dur_a_coeffs:
			file.write(";".join(map(str, i)) + "\n")
	print("saved all")


def load_plots(num):
	# Plot new thresholded data
	t, f = divmod(num, n_files)
	durations, areas = events[f][t]
	q_bins, q_pdf = pdf(np.log10(quiets[f][t]), 10)
	dur_bins, dur_pdf = pdf(np.log10(durations), 10)
	a_bins, a_pdf = pdf(np.log10(areas), 10)

	dur_a_plot.loglog_plot(durations[::2], areas[::2])
	q_pdf_plot.loglog_plot(10 ** q_bins, q_pdf)
	dur_pdf_plot.loglog_plot(10 ** dur_bins, dur_pdf)
	a_pdf_plot.loglog_plot(10 ** a_bins, a_pdf)

	text.setText(f"Threshold {t+1}/{n_thresholds}, file {f+1}/{n_files}")


# Load data before analysing
events = [
	categorized_series_from_file(f"data/{datadir}/{f}.e", 2, [int, int], 0, [1, 2])
	for f in tqdm(range(n_files))
]
quiets = [
	categorized_series_from_file(f"data/{datadir}/{f}.q", 1, [int], 0, [1])
	for f in tqdm(range(n_files))
]
# Close spectral density analysis plot
crit_freq_plot.close()

# Add new plots, reset counter and rebind buttons
dur_a_plot = LinearRegionPlot(2, title="durations v area")
q_pdf_plot = LinearRegionPlot(6, title="pdf of quiet-times")
dur_pdf_plot = LinearRegionPlot(6, title="pdf of durations")
a_pdf_plot = LinearRegionPlot(6, title="pdf of areas")

btn_runfile = Button("Lock and finish for current file")

text = pg.LabelItem()

win.removeItem(crit_freq_plot)
win.removeItem(btn_next)
win.removeItem(btn_run)
btn_next.sigPressed.disconnect()
btn_run.sigPressed.disconnect()

counter = 1

win.addItem(text, row=0, col=0, colspan=3)
win.addItem(btn_next, row=3, col=0, colspan=3)
win.addItem(btn_run, row=5, col=0, colspan=3)
win.addItem(btn_runfile, row=4, col=0, colspan=3)
win.addItem(a_pdf_plot, row=1, col=0)
win.addItem(dur_pdf_plot, row=1, col=1)
win.addItem(q_pdf_plot, row=2, col=0)
win.addItem(dur_a_plot, row=2, col=1)

# Load first batch
load_plots(0)

btn_next.sigPressed.connect(advance)
btn_run.sigPressed.connect(lock_and_run_all)
btn_runfile.sigPressed.connect(lock_and_run_file)

input()
win.close()
