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
	d, U = np.linalg.eig(cov)
	L = np.diagflat(d)
	A = np.dot(U, np.sqrt(L))
	X = np.random.randn(len(mean), n)
	return (np.dot(A,X) + np.tile(mean, n))

if __name__ == '__main__':
	samples = 1000
	mean = [[0],[1],[2],[-1]]
	cov  = [[1,0,-3,2],[0,1,2,-3],[-2,0,0,1],[9,3,-4,2]]

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