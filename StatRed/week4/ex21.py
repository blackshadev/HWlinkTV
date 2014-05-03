""" StatRed: Week 4 Opdr 21 
" 
" Authors: Tessa Klunder & Vincent Hagen
" Date   : 29-4-2014
"
" Plots multivariant normal distributed values for a given mu and sigma
" It plots these values as a nxn matrix of plots where the index within 
" the matrix (i, j) matches the dimension which are plotted against each other 
"
"""

import numpy as np
import matplotlib.pyplot as plt

# Returns n samples of normal distributed random variables with given
# mean and covariance
def multivariate(mean, cov, n):
	d, U = np.linalg.eigh(cov)
	L = np.diagflat(d)
	A = np.dot(U, np.sqrt(L))
	X = np.random.randn(len(mean), n)
	return (np.dot(A,X) + np.tile(mean, n))

if __name__ == '__main__':
	samples = 1000
	mean = [[0],[1],[2],[-1]]

	# Overgenomen van R. Wolferink
	cov = [[  3.01602775,   1.02746769,  -3.60224613,  -2.08792829],
           [  1.02746769,   5.65146472,  -3.98616664,   0.48723704],
           [ -3.60224613,  -3.98616664,  13.04508284,  -1.59255406],
           [ -2.08792829,   0.48723704,  -1.59255406,   8.28742469]]

	Y = multivariate(mean, cov, samples)

	fig, axes = plt.subplots(nrows=4, ncols=4)
	fig.subplots_adjust(hspace=0.05, wspace=0.05)

	for i in range(0,4):
		for j in range(0,4):
			ax = axes[i, j]
			# No axes for clarity in the plot
			ax.xaxis.set_visible(False)
			ax.yaxis.set_visible(False)
			#skip the diagonal
			if i == j: continue
			
			ax.scatter(Y[i], Y[j])

	plt.show()