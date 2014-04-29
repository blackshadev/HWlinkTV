import numpy as np
import matplotlib.pyplot as plt

def multivariate(mean, cov, n):
	d, U = np.linalg.eig(cov)
	L = np.diagflat(d)
	A = np.dot(U, np.sqrt(L))
	X = np.random.randn(4, n)
	return (np.dot(A,X) + np.tile(mean, n))

def plot(ax, X, i, j):
	ax.scatter(X[i], X[j])

if __name__ == '__main__':
	size = 1000
	mean = [[0],[1],[2],[-1]]
	cov = [[1,0,-3,2],[0,1,2,-3],[-2,0,0,1],[9,3,-4,2]]

	Y = multivariate(mean, cov, size)

	count = 0
	plt.figure()
	fig, axes = plt.subplots(nrows=4, ncols=4)
	fig.subplots_adjust(hspace=0.05, wspace=0.05)

	for i in range(0,4):
		for j in range(0,4):
			ax = axes[i, j]
			ax.xaxis.set_visible(False)
			ax.yaxis.set_visible(False)

			if i == j: continue
			
			plot(ax, Y, i, j)
			count += 1
	plt.show()