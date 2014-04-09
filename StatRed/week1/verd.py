"""
StatRed Inf 2 - 2014

Students: Tessa Klunder, Vincent Hagen

Week 1 Assignment 3
"""

import scipy
from scipy.stats import norm
import numpy as np
import matplotlib.pyplot as plt


def showPdf(rv):
    x = np.linspace(-5* si, 5 * si, 100 * si)
    h = plt.plot(x, rv.pdf(x))

def showCdf(rv):
    x = np.linspace(-5* si, 5 * si, 100 * si)
    h = plt.plot(x, rv.cdf(x))

"""
Plots the pdf and picks n random values, plots these values
These values are automaticly noralised by using scipy.stats.norm.rvs func
"""
def randNorm(rv, n):
    showPdf(rv)
    R = rv.rvs(n)
    n, bins, patches = plt.hist(R, 50, normed=True)

if __name__ == '__main__':

    mu = 1
    si = 1
    n = 1000

    rv = norm(loc=mu,scale=si)
    randNorm(rv, n)
    # showCdf(rv)
    plt.show(rv)