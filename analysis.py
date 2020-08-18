from tqdm import tqdm
from scipy.signal import welch
from definitions import thresholds_gen, n_thresholds
import numpy as np

datadir = "prange_5e-6"
# number of trials to analyse - each with different probability values
n_files = 20
for i in range(n_files):
	dur = 0
	area = 0

	crits = []

	# Load data file and store data in 'crits'
	with open(f"./data/{datadir}/{i}.d", "r") as raw:
		for line in tqdm(raw.readlines()[3:], desc=f"loading crits ({i})"):
			strs = line.rstrip(";\n\r ").split(";")
			crit = int(strs[0])
			crits.append(crit)

	N = len(crits)
	# Calculate threshold values form the standard deviation of 'crits'
	std = np.std(crits)
	thresholds = thresholds_gen(std)

	# Initiate lists used in analysis
	durations = [0 for j in range(n_thresholds)]
	areas = [0 for j in range(n_thresholds)]
	quiets = [0 for j in range(n_thresholds)]
	peaked = [False for j in range(n_thresholds)]

	# Estimate spectral density of 'crits' signal
	freq, density = welch(crits, nperseg=N / 10000)

	# Save spectral density data to file
	with open(f"./data/{datadir}/{i}.f", "w") as freqfile:
		for f, s in zip(freq, density):
			freqfile.write(f"{f};{s}\n")

	# Calculate quiet times between spikes as well as durations and areas of spikes
	# This is written directly to file
	with open(f"./data/{datadir}/{i}.e", "w") as eventfile, open(
		f"./data/{datadir}/{i}.q", "w"
	) as quietfile:
		for crit in tqdm(crits):
			for t, threshold in enumerate(thresholds):
				if crit <= threshold and durations[t] > 0:
					eventfile.write(f"{t};{durations[t]};{areas[t]}\n")
					durations[t] = 0
					areas[t] = 0
					peaked[t] = True
				elif crit > threshold:
					durations[t] += 1
					areas[t] += crit
				if crit <= threshold and peaked[t]:
					quiets[t] += 1
				elif crit > threshold and quiets[t] > 0:
					quietfile.write(f"{t};{quiets[t]}\n")
					quiets[t] = 0

	# Save threshold values to file
	with open(f"./data/{datadir}/{i}.t", "w") as threshfile:
		threshfile.write(";".join(map(str, thresholds)))
