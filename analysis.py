import sys
from colorsys import hsv_to_rgb

import numpy as np
import pyqtgraph as pg
from PyQt5 import QtGui
from tqdm import tqdm


def simple_plot(window, data, *args, size=4, color='w', log_x=False, log_y=False, **kwargs):
	plot_kwargs = {'symbolSize': size}
	if len(args) > 0:
		plot_kwargs['pen'] = None
		plot_kwargs['symbolPen'] = None
		plot_kwargs['symbolBrush'] = color
		plot_kwargs['symbol'] = 'o'
	else:
		plot_kwargs['pen'] = color
	plot = window.addPlot(**kwargs)
	plot.setLogMode(log_x, log_y)
	plot.plot(data, *args, **plot_kwargs)


crits = []
added = []
lost = []
total = []

with open('./output.txt', 'r') as file:
	for line in tqdm(file.readlines()[3:]):
		strs = line.rstrip(';\n\r ').split(';')
		crits.append(int(strs[0]))
		added.append(int(strs[1]))
		lost.append(int(strs[2]))
		total.append(int(strs[3]))

n_thresholds = 9
stddev = np.std(crits)
thresholds = [0] + [stddev * (10**(0.2 * (i - 4)))
                    for i in range(n_thresholds - 1)]
colors = [tuple(map(lambda x: 255 * x, hsv_to_rgb((i + 1) / n_thresholds, 1, 1)))
          for i in range(n_thresholds)]

durations = [[] for i in range(n_thresholds)]
areas = [[] for i in range(n_thresholds)]
dur = [0] * n_thresholds
area = [0] * n_thresholds

for crit in tqdm(crits):
	for i in range(n_thresholds):
		if crit <= thresholds[i] and dur[i] > 0:
			durations[i].append(dur[i])
			areas[i].append(area[i])
			dur[i] = 0
			area[i] = 0
		elif crit > thresholds[i]:
			dur[i] += 1
			area[i] += crit

pg_app = QtGui.QApplication(sys.argv)
win = pg.GraphicsWindow()

crit_plot = win.addPlot(title='crits', row=1, col=0, colspan=2)
ca_plot = win.addPlot(
	title='thresholded durations v area', row=0, col=0)
ca_plot.setLogMode(True, True)
pdf_plot = win.addPlot(
	title='thresholded pdf for durations', row=0, col=1)
pdf_plot.setLogMode(True, True)


crit_plot.plot(crits)
for threshold, color, duration, area in zip(tqdm(thresholds), colors, durations, areas):
	crit_plot.plot([0, len(crits)], [threshold, threshold],
	               pen=pg.mkPen(color, width=2))
	ca_plot.plot(duration, area, symbolSize=1, symbol='o',
	             symbolPen=None, symbolBrush=color, pen=None)
	dpdf, edges = np.histogram(duration, bins=50, density=True)
	bins = [(edges[i] + edges[i + 1]) / 2 for i in range(len(edges) - 1)]
	dpdf = list(dpdf)
	for i in reversed(range(len(dpdf))):
		if dpdf[i] == 0:
			del dpdf[i]
			del bins[i]
	pdf_plot.plot(bins, dpdf, symbolSize=4, symbol='o',
               symbolPen=None, symbolBrush=color, pen=None)
	# simple_plot(win, bins, dpdf, size=4, log_x=True, log_y=True,
	#             title='thresholded durations pdf', row=1, col=1, color='r')


# simple_plot(win, durations, areas, size=1, log_x=True, log_y=True,
#             title='durations v area', row=0, col=0)

# dpdf, edges = np.histogram(durations, bins=50, density=True)
# bins = [(edges[i] + edges[i + 1]) / 2 for i in range(len(edges) - 1)]
# dpdf = list(dpdf)
# for i in reversed(range(len(dpdf))):
# 	if dpdf[i] == 0:
# 		del dpdf[i]
# 		del bins[i]
# simple_plot(win, bins, dpdf, size=4, log_x=True, log_y=True,
#             title='durations pdf', row=0, col=1)

pg_app.exec_()
