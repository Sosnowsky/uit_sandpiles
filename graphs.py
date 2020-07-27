import sys
from colorsys import hsv_to_rgb
from string import digits

import numpy as np
import pyqtgraph as pg
from PyQt5 import QtGui
from tqdm import tqdm

thresholds = [0, 3.3, 6.6, 13.2, 26.3, 52.6, 104.9]


def simple_plot(
	window, data, *args, size=4, pen="w", log_x=False, log_y=False, **kwargs
):
	plot_kwargs = {"symbolSize": size}
	if len(args) > 0:
		plot_kwargs["pen"] = None
		plot_kwargs["symbolPen"] = None
		plot_kwargs["symbolBrush"] = pen
		plot_kwargs["symbol"] = "o"
	else:
		plot_kwargs["pen"] = pen
	plot = window.addPlot(**kwargs)
	plot.setLogMode(log_x, log_y)
	return plot.plot(data, *args, **plot_kwargs)


def line_on_plot(plot, line, pen="w"):
	a, b = line
	xs = plot.getAxis("bottom").range
	ys = list(map(lambda x: a * x + b, xs))
	return plot.plot(xs, ys, pen=pen)


colors = [
	tuple(map(lambda x: 255 * x, hsv_to_rgb((i + 1) / len(thresholds), 1, 1)))
	for i in range(len(thresholds))
]

durations = [[] for i in thresholds]
areas = [[] for i in thresholds]

with open("./data/analysed.txt", "r") as file:
	for line in tqdm(file.readlines()[3:]):
		sp1 = line.rstrip("\n").split(":")
		sp2 = sp1[1].split(",")
		idx = int(sp1[0])
		durations[idx].append(int(sp2[0]))
		areas[idx].append(int(sp2[1]))


pg_app = QtGui.QApplication(sys.argv)
win = pg.GraphicsWindow()

ca_plot = win.addPlot(title="thresholded durations v area", row=0, col=0)
# ca_plot.setLogMode(True, True)
pdf_plot = win.addPlot(title="thresholded pdf for durations", row=0, col=1)
# pdf_plot.setLogMode(True, True)
# rsq_plot = win.addPlot(title='rsq', row=0, col=2)
# d2_rsq_plot = win.addPlot(title='d2_rsq', row=1, col=2)

lines = []
scatters = []

for threshold, color, duration, area in zip(tqdm(thresholds), colors, durations, areas):
	ca_plot.plot(
		np.log10(duration),
		np.log10(area),
		symbolSize=1,
		symbol="o",
		symbolPen=None,
		symbolBrush=color + (160,),
		pen=None,
	)
	dpdf, edges = np.histogram(duration, bins=50, density=True)
	bins = [(edges[i] + edges[i + 1]) / 2 for i in range(len(edges) - 1)]
	dpdf = list(dpdf)
	bins = list(bins)
	for i in reversed(range(len(dpdf))):
		if dpdf[i] == 0:
			del dpdf[i]
			del bins[i]
	dpdf = np.log10(dpdf)
	bins = np.log10(bins)
	scatters.append(
		pdf_plot.plot(
			bins,
			dpdf,
			symbolSize=4,
			symbol="o",
			symbolPen=None,
			symbolBrush=color + (160,),
			pen=None,
		)
	)

	for i in range(len(dpdf) - 2):
		linreg, square = np.polyfit(bins[i:], dpdf[i:], 1, full=True)[:2]
		if i > 0:
			d_square = (square[0] - p_square) / (bins[i] - bins[i - 1])
			if i > 1:
				d2_square = (d_square - p_d_square) / (bins[i] - bins[i - 1])
				if i > 2 and (d2_square - p_d2_square) / (bins[i] - bins[i - 1]) >= 500:
					idx0 = i
					break
				p_d2_square = d2_square
			p_d_square = d_square
		p_square = square[0]
	lines.append(line_on_plot(pdf_plot, linreg, pen=color))
	print(linreg)
	# pdf_plot.plot((bins[idx0], bins[idx0]), (-1, -7), pen=color)

while 1:
	text = input()
	try:
		if text == "q":
			break
		elif text == "a":
			for s, l in zip(scatters, lines):
				s.show()
				l.show()
		elif text[0] == "s":
			for i in text.split(" ")[1:]:
				lines[int(i)].show()
				scatters[int(i)].show()
		elif text[0] == "h":
			for i in text.split(" ")[1:]:
				lines[int(i)].hide()
				scatters[int(i)].hide()
		elif text[0] in digits:
			for s, l in zip(scatters, lines):
				s.hide()
				l.hide()
			for i in text.split(" "):
				scatters[int(i)].show()
				lines[int(i)].show()
	except KeyboardInterrupt:
		break
	except:
		print("error")
