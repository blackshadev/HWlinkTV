import numpy as np
import matplotlib.pyplot as plt

def random_uniform():
	return np.random.uniform(low=0.0, high=1.0, size=1)

def compute(u):
	return -np.log(u)


if __name__ == '__main__':
	n = 10000

	u = random_uniform()
	X = np.random.uniform(0,1,n)
	X = compute(X) 
	count, bins, ignore = plt.hist(X, 25, normed=True)
	mean = np.mean(X)
	print "Geschatte lambda: %s" % (1/mean) 
	plt.show()