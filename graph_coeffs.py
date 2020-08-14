import pyqtgraph as pg
import numpy as np
# from pyqtgraph.exporters import SVGExporter
from pyqtgraph import QtCore

# number of trials run
n_files = 20

# Create window for graphs
win = pg.GraphicsLayoutWidget(title="Coefficients")
r_win = pg.GraphicsLayoutWidget(title="Color legend")
flags = QtCore.Qt.WindowFlags(QtCore.Qt.WindowStaysOnTopHint)
r_win.setWindowFlags(flags)

# List of probabilities used in trials
# This should not be hard coded -sorry
probs = [(i + 1) * 5e-6 for i in range(n_files)]
thresholds = []

# Read threshold values from file
for i in range(n_files):
	with open(f"data/prange_5e-6/{i}.t", "r") as file:
		subs = file.readlines()[0].split(";")
		thresholds.append(list(map(int, subs)))


def tplots(fname, title):
	# Plot the coefficients that depend on a threshold as well as a probability
	win.addItem(pg.LabelItem(title, size="18pt"), col=0, colspan=2)
	win.nextRow()
	p1 = win.addPlot(col=0, labels={"left": "coefficient", "bottom": "probability"})
	p2 = win.addPlot(col=1, labels={"bottom": "threshold"})
	win.nextRow()
	data = []
	with open(fname, "r") as file:
		for i, line in enumerate(file.readlines()):
			subs = line.split(";")
			data.append(list(map(float, subs)))
		tp = np.transpose(data)
		tL = len(tp)
		L = len(data)
		for i, d in enumerate(data):
			p1.plot(probs, d, pen=(i, L + tL))

		for i, d in enumerate(tp):
			p2.plot(thresholds[i], d, pen=(L + i, L + tL))


p0 = r_win.addPlot(row=0, col=0, title="thresholds")
p0.hideAxis("left")
max_t = max(thresholds, key=lambda l: l[-1])
min_t = min(thresholds, key=lambda l: l[-1])
L = len(min_t)
tL = len(probs)
span = 1.0 / L
for i, bounds in enumerate(zip(min_t, max_t)):
	c = pg.intColor(i, L + tL)
	pen = pg.mkPen(c, width=4)
	reg = pg.LinearRegionItem(
		bounds, brush=c, pen=pen, movable=False, span=(span * i, span * (i + 1))
	)
	p0.addItem(reg)
	p0.setMaximumHeight(130)

p1 = r_win.addPlot(row=1, col=0, title="probabilities")
p1.hideAxis("left")
for i, p in enumerate(probs):
	reg = pg.InfiniteLine(p, pen=pg.mkPen((L + i, L + tL), width=10))
	p1.addItem(reg)
	p1.setMaximumHeight(70)

tplots("data/prange_5e-6/dur_a.c", "duration v. area")
tplots("data/prange_5e-6/a_pdf.c", "area distribution")
tplots("data/prange_5e-6/dur_pdf.c", "duration distribution")
tplots("data/prange_5e-6/q_pdf.c", "quiet-time distribution")

# The spectral density estimation does not rely on thresholds - so we dont use 'tplots()'
win.nextRow()
win.addItem(pg.LabelItem("Spectral density", size="18pt"), col=0, colspan=2)
win.nextRow()
p = win.addPlot(
	col=0, colspan=2, labels={"left": "coefficients", "bottom": "probability"}
)
with open("data/prange_5e-6/freq.c", "r") as file:
	data = list(map(float, file.readlines()))

p.plot(probs, data, pen="r")

win.showMaximized()
r_win.show()
r_win.resize(400, 240)


input()
win.close()
r_win.close()
