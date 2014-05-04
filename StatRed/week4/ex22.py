""" StatRed: Week 4 Opdr 22 
" 
" Authors: Tessa Klunder & Vincent Hagen
" Date   : 30-4-2014
"
" Plots multivariant normal distributed values for a given mu and sigma.
" It then estimates the values of the mean and the covariance. 
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
    X = np.random.randn(4, n)
    return (np.dot(A,X) + np.tile(mean, n))

def mean_estimator(Y):
    return np.mean(Y, 1)

# Estimates the covariance 
def cov_estimator(Y, mean_est):
    n = Y.shape[1]
    Yzm = Y - np.tile(mean_est[:,np.newaxis], n)
    return np.dot(Yzm, np.transpose(Yzm)) / (n-1)

def plot(ax, X, i, j):
    ax.scatter(X[i], X[j])

if __name__ == '__main__':
    size = 1000
    mean = [[0],[1],[2],[-1]]
    # Acquired from R. Wolferink
    cov = [[  3.01602775,   1.02746769,  -3.60224613,  -2.08792829],
           [  1.02746769,   5.65146472,  -3.98616664,   0.48723704],
           [ -3.60224613,  -3.98616664,  13.04508284,  -1.59255406],
           [ -2.08792829,   0.48723704,  -1.59255406,   8.28742469]]

    Y = multivariate(mean, cov, size)

    mean_est = mean_estimator(Y)
    cov_est = cov_estimator(Y, mean_est)

    print("mean est.:"); print mean_est
    print("covariance est.:"); print cov_est
