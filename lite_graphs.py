import numpy as np
import pyqtgraph as pg
from more_itertools import pairwise


def line_on_plot(plot, line, pen="w"):
	a, b = line
	xs = plot.getAxis("bottom").range
	ys = list(map(lambda x: a * x + b, xs))
	return plot.plot(xs, ys, pen=pen)


def loglog(x, y):
	x = np.array(x)
	y = np.array(y)
	mask = (x != 0) & (y != 0)
	return np.log10(x[mask]), np.log10(y[mask])


def rad_cutoff(x, y, low_cutoff, high_cutoff):
	mask = (x ** 2 + y ** 2 > np.square(low_cutoff).sum()) & (
		x ** 2 + y ** 2 < np.square(high_cutoff).sum()
	)
	return mask


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
	if type(l_lim) == tuple:
		mask = rad_cutoff(log_x, log_y, l_lim, u_lim)
	else:
		mask = (log_x > l_lim) & (log_x < u_lim)

	val_x = log_x[mask]
	val_y = log_y[mask]
	inval_x = log_x[~mask]
	inval_y = log_y[~mask]

	line = np.polyfit(val_x, val_y, 1)

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

	line_on_plot(plot, line, "b")


win = pg.GraphicsWindow()

dur_a_plot = win.addPlot(title="durations v area", row=1, col=0)
dur_pdf_plot = win.addPlot(title="pdf of durations", row=0, col=1)
a_pdf_plot = win.addPlot(title="pdf of areas", row=0, col=0)
crit_freq_plot = win.addPlot(title="frequency spectrum of # of crits", row=1, col=1)


durations, areas = series_from_file("data/p0.0001_256/events.txt", 2, dtype=int)
generic_loglog(durations, areas, dur_a_plot, (1.5, 1.5), (3.5, 5.5), 1)

freq, density = series_from_file("data/p0.0001_256/nps10000.txt", 2, dtype=float)
generic_loglog(freq, density, crit_freq_plot, -2.6, -0.5, 3)

dur_bins, dur_pdf = pdf(durations, 1000)
generic_loglog(dur_bins, dur_pdf, dur_pdf_plot, 1.9, 3, 3)

a_bins, a_pdf = pdf(areas, 1000)
generic_loglog(a_bins, a_pdf, a_pdf_plot, 3.7, 5, 3)

input()
