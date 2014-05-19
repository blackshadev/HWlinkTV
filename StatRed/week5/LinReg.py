""" StatRed: Week 5 Opdr 7 
" 
" Authors: Tessa Klunder & Vincent Hagen
" Date   : 19-5-2014
"
" Program to find the non-linear model with regression.
"
"""

from pylab import linspace, randn, ones, vstack, plot, savefig, dot, norm
from scipy.optimize import minimize
import numpy as np

th1 = 2
th2 = .5
th = [th1, th2]
rndVar = 0.3

# The given non-linear model that we need to estimate.
def fn(x, th):
	return th[0] * np.sin(th[1] * x)

# Generate noisy data by using the given model function and adding a random
# value.
x = linspace(0,10,100)
y = fn(x, th) + rndVar * np.random.randn(*x.shape)
X = vstack((ones(x.shape),x)).T

# The minimized function of fn().
def J(th):
	return np.sum((y - fn(x, th))**2)

# Returns the gradient of J as a vector
def Jac(th):
	dth1 = np.sum(2 * np.sin(x * th[1]) * (th[0] * np.sin(x * th[1]) - y))
	dth2 = np.sum(2 * x * th[0] * np.cos(x * th[1]) * (th[0] * np.sin(x * th[1]) - y))
	return np.array([dth1, dth2])

# minimize() gives the vector for the estimated th1 and th2. It finds these by
# calculating the values that give the lowest output of J. The second argument
# (3, .65) is an estimation made by us beforehand. 
res = minimize(J, (3, .65), jac=Jac, method='CG')
print res

eth1, eth2 = res.x
plot(x, y, 'xb')
plot(x, fn(x, [eth1, eth2]), 'b')
plot(x, fn(x, th), 'g')
savefig('linregression.png')