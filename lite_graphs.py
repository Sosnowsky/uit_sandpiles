import numpy as np
import pyqtgraph as pg
from tqdm import tqdm


def line_on_plot(plot, line, pen="w"):
	a, b = line
	xs = plot.getAxis("bottom").range
	ys = list(map(lambda x: a * x + b, xs))
	return plot.plot(xs, ys, pen=pen)


durations = []
areas = []

with open("./data/p0.0001_256/analysed.txt", "r") as file:
	for line in tqdm(file.readlines()[3::2]):
		sp1 = line.rstrip("\n").split(":")
		if int(sp1[0]) == 0:
			sp2 = sp1[1].split(",")
			durations.append(int(sp2[0]))
			areas.append(int(sp2[1]))


win = pg.GraphicsWindow()

ca_plot = win.addPlot(title="thresholded durations v area", row=0, col=0)
pdf_plot = win.addPlot(title="thresholded pdf for durations", row=0, col=1)

log_durations = np.log10(durations)
log_areas = np.log10(areas)

ca_filter = (log_durations ** 2 + log_areas ** 2 > 2 * 1.5 * 1.5) & (
	log_durations ** 2 + log_areas ** 2 < 3.5 * 3.5 + 5.5 * 5.5
)

f_log_durations = log_durations[ca_filter]
f_log_areas = log_areas[ca_filter]

ca_plot.plot(
	f_log_durations,
	f_log_areas,
	symbolSize=1,
	symbol="o",
	symbolPen=None,
	symbolBrush="r",
	pen=None,
)

ca_plot.plot(
	log_durations[~ca_filter],
	log_areas[~ca_filter],
	symbolSize=1,
	symbol="o",
	symbolPen=None,
	symbolBrush="g",
	pen=None,
)

ca_line = np.polyfit(f_log_durations, f_log_areas, 1)
line_on_plot(ca_plot, ca_line, "y")

dpdf, edges = np.histogram(durations, bins=50, density=True)
bins = np.array([(edges[i] + edges[i + 1]) / 2 for i in range(len(edges) - 1)])
dpdf_filter = dpdf != 0
dpdf = dpdf[dpdf_filter]
bins = bins[dpdf_filter]

log_dpdf = np.log10(dpdf)
log_bins = np.log10(bins)

for i in range(len(log_dpdf) - 2):
	linreg, square = np.polyfit(log_bins[i:], log_dpdf[i:], 1, full=True)[:2]
	if i > 0:
		d_square = (square[0] - p_square) / (log_bins[i] - log_bins[i - 1])
		if i > 1:
			d2_square = (d_square - p_d_square) / (log_bins[i] - log_bins[i - 1])
			if i > 2 and (d2_square - p_d2_square) / (log_bins[i] - log_bins[i - 1]) >= 500:
				idx0 = i
				break
			p_d2_square = d2_square
		p_d_square = d_square
	p_square = square[0]


pdf_plot.plot(
	log_bins[idx0:],
	log_dpdf[idx0:],
	symbolSize=4,
	symbol="o",
	symbolPen=None,
	symbolBrush="g",
	pen=None,
)

pdf_plot.plot(
	log_bins[:idx0],
	log_dpdf[:idx0],
	symbolSize=4,
	symbol="o",
	symbolPen=None,
	symbolBrush="r",
	pen=None,
)
line_on_plot(pdf_plot, linreg, pen="y")


input()
