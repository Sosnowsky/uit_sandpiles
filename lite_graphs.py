import numpy as np
import pyqtgraph as pg
from pyqtgraph import QtGui, QtCore
from more_itertools import pairwise


class Button(QtGui.QGraphicsProxyWidget):
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
	sigDragged = QtCore.Signal(object)

	def __init__(self, *args, **kwargs):
		self.beta = None
		pg.PlotItem.__init__(self, *args, **kwargs)
		self.region = pg.LinearRegionItem()
		self.addItem(self.region)
		self.region.sigRegionChangeFinished.connect(self.emitSig)

	def emitSig(self):
		self.sigDragged.emit(self)

	def clear(self):
		pg.PlotItem.clear(self)
		self.addItem(self.region)
		if self.legend is not None:
			self.legend.clear()

	def getRegion(self):
		return self.region.getRegion()


def line_on_plot(plot, line, pen="w", name=None):
	a, b = line
	xs = plot.getAxis("bottom").range
	ys = list(map(lambda x: a * x + b, xs))
	return plot.plot(xs, ys, pen=pen, name=name)


def loglog(x, y):
	x = np.array(x)
	y = np.array(y)
	mask = (x != 0) & (y != 0)
	return np.log10(x[mask]), np.log10(y[mask])


def pdf(x, bins):
	pdf, edges = np.histogram(x, bins=bins, density=True)
	bins = np.array([(e1 + e2) / 2 for e1, e2 in pairwise(edges)])
	return bins, pdf


def series_from_file(fname, n_series, dtype):
	data = [] if n_series == 1 else [[] for i in range(n_series)]
	with open(fname, "r") as file:
		for line in file.readlines():
			if n_series == 1:
				data.append(dtype(line))
			else:
				split = line.split(";")
				for d, s in zip(data, split):
					d.append(dtype(s))
	return data


def generic_loglog(x, y, plot, l_lim, u_lim, size):
	log_x, log_y = loglog(x, y)
	mask = (log_x > l_lim) & (log_x < u_lim)

	val_x = log_x[mask]
	val_y = log_y[mask]
	inval_x = log_x[~mask]
	inval_y = log_y[~mask]

	plot.plot(
		val_x, val_y, symbolSize=size, symbol="o", symbolPen=None, symbolBrush="g", pen=None,
	)

	plot.plot(
		inval_x,
		inval_y,
		symbolSize=size,
		symbol="o",
		symbolPen=None,
		symbolBrush="r",
		pen=None,
	)

	plot.autoRange()
	dur_a_plot.disableAutoRange()

	try:
		line, (r2,) = np.polyfit(val_x, val_y, 1, full=True)[:2]
		line_on_plot(plot, line, "b", name=str(r2))
	except:
		line = None

	if line is not None:
		plot.beta = line[0]
	else:
		plot.beta = None


win = pg.GraphicsWindow()
win.show()


dur_a_plot = LinearRegionPlot(title="durations v area")
dur_pdf_plot = LinearRegionPlot(title="pdf of durations")
a_pdf_plot = LinearRegionPlot(title="pdf of areas")
crit_freq_plot = LinearRegionPlot(title="frequency spectrum of # of crits")
btn = Button("next")


win.addItem(dur_a_plot, row=1, col=0)
win.addItem(dur_pdf_plot, row=0, col=1)
win.addItem(a_pdf_plot, row=0, col=0)
win.addItem(crit_freq_plot, row=1, col=1)
win.addItem(btn, row=3, col=0, colspan=2)


def button_callback():
	global fnum
	durations, areas = series_from_file(f"data/prange_5e-5/{fnum}.e", 2, dtype=int)
	freq, density = series_from_file(f"data/prange_5e-5/{fnum}.f", 2, dtype=float)
	dur_bins, dur_pdf = pdf(durations, 1000)
	a_bins, a_pdf = pdf(areas, 1000)
	data = [[durations, areas], [freq, density], [dur_bins, dur_pdf], [a_bins, a_pdf]]

	print(dur_a_plot.beta)

	def setCallback(plot, x, y, s):
		def callback(p):
			p.clear()
			generic_loglog(x, y, p, *p.getRegion(), s)

		plot.sigDragged.connect(callback)

	setCallback(dur_a_plot, durations, areas, 1)
	setCallback(dur_pdf_plot, dur_bins, dur_pdf, 2)
	setCallback(a_pdf_plot, a_bins, a_pdf, 2)
	setCallback(crit_freq_plot, freq, density, 2)

	for plot, d in zip(win.ci.items.keys(), data):
		if plot is not btn:
			plot.addLegend()
			plot.emitSig()

	fnum += 1
	if fnum == 20:
		win.close()
		exit()


fnum = 0
btn.sigPressed.connect(button_callback)

input()
win.close()
