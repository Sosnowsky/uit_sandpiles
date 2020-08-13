def thresholds_gen(std):
	return [0] + [int(std * (10 ** (j / 10))) for j in range(-5, 7)]


n_thresholds = len(thresholds_gen(0))
