import pyqtgraph as pg
import numpy as np

# number of trials run
n_files = 20

# Create window for graphs
win = pg.GraphicsLayoutWidget()

# List of probabilities used in trials
# This should not be hard coded -sorry
probs = [(i + 1) * 5e-6 for i in range(n_files)]
thresholds = []

# Read threshold values from file
for i in range(n_files):
	with open(f"data/prange_5e-6/{i}.t", "r") as file:
		subs = file.readlines()[0].split(";")
		thresholds.append(list(map(int, subs)))


def tplots(fname):
	# Plot the coefficients that depend on a threshold as well as a probability
	p1 = win.addPlot(col=0)
	p2 = win.addPlot(col=1)
	win.nextRow()
	win.show()
	data = []
	with open(fname, "r") as file:
		for i, line in enumerate(file.readlines()):
			subs = line.split(";")
			data.append(list(map(float, subs)))
		L = len(data)
		for i, d in enumerate(data):
			p1.plot(probs, d, pen=(i, L))

		tp = np.transpose(data)
		tL = len(tp)
		for i, d in enumerate(tp):
			p2.plot(thresholds[i], d, pen=(i, tL))


tplots("data/prange_5e-6/dur_a.c")
tplots("data/prange_5e-6/a_pdf.c")
tplots("data/prange_5e-6/dur_pdf.c")
tplots("data/prange_5e-6/q_pdf.c")

# The spectral density estimation does not rely on thresholds - so we dont use 'tplots()'
win.nextRow()
p = win.addPlot(colspan=2)
with open("data/prange_5e-6/freq.c", "r") as file:
	data = list(map(float, file.readlines()))

p.plot(probs, data)


input()
win.close()
