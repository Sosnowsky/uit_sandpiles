from tqdm import tqdm

thresholds = [0, 3.3, 6.6, 13.2, 26.3, 52.6, 104.9]

durations = [[] for i in thresholds]
areas = [[] for i in thresholds]
dur = [0] * len(thresholds)
area = [0] * len(thresholds)

with open("./data/9.d", "r") as raw, open("./analysed.txt", "w") as out:
	for line in tqdm(raw.readlines()[3:]):
		strs = line.rstrip(";\n\r ").split(";")
		crit = int(strs[0])
		for i in range(len(thresholds)):
			if crit <= thresholds[i] and dur[i] > 0:
				durations[i].append(dur[i])
				areas[i].append(area[i])
				out.write(f"{i}: {dur[i]}, {area[i]}\n")
				dur[i] = 0
				area[i] = 0
			elif crit > thresholds[i]:
				dur[i] += 1
				area[i] += crit
