""" StatRed: Week 3 Opdr 3 
" 
" Authors: Tessa Klunder & Vincent Hagen
" Date   : 19-4-2014
"
" Transforms an random uniform distribution to an exponential distribution.
" Plots n samples of the exponential distribution in bins
"""

import numpy as np
import matplotlib.pyplot as plt

# Tranforms random uniform distributed values in U, (0 <= u_i <= 1). 
def compute(U):
	return -np.log(U)


if __name__ == '__main__':
	n = 10000

	# random values
	X = np.random.uniform(0,1,n)
	X = compute(X) 

	# plot
	count, bins, ignore = plt.hist(X, 25, normed=True)
	
	# Estimate lambda
	mean = np.mean(X)
	print "Geschatte lambda: %s" % (1/mean) 
	
	plt.show()