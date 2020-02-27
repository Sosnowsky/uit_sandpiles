import matplotlib.pyplot as plt
import numpy as np

crits = []
added = []
lost = []
total = []

with open('data/output.txt', 'r') as file:
	for line in file.readlines()[3:]:
		strs = line.rstrip(';\n\r ').split(';')
		crits.append(int(strs[0]))
		added.append(int(strs[1]))
		lost.append(int(strs[2]))
		total.append(int(strs[3]))

durations = []
areas = []
dur = 0
area = 0
for i, v in enumerate(crits):
	if v == 0 and dur > 0:
		durations.append(dur)
		areas.append(area)
		dur = 0
		area = 0
	elif v != 0:
		dur += 1
		area += v

plt.loglog(durations, areas, 'o', markersize=3)
plt.show()
pdf, edges = np.histogram(durations, bins=50, density=True)
bins = [(edges[i] + edges[i + 1]) / 2 for i in range(len(edges) - 1)]
plt.loglog(bins, pdf, 'o', markersize=3)
plt.show()
