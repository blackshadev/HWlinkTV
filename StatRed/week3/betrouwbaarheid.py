""" StatRed: Week 3 Confidence 
" 
" Authors: Tessa Klunder & Vincent Hagen
" Date   : 19-4-2014
"
" Uses data in tijden.log.
" Calculating confidence intervals for estimator means of data samples.
" Plots the confidence intervals as errorbars around the estimated mean,
"  and plots the real mean (mean of the whole data set).
" The program prints the percentage of times the estimated mean lies within the 
"  range (calculated with errBound) of the real mean
"""

import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt
import random

class Confidence:
    __dict__ = ["data","mean"]
    def __init__(self, data):
        self.data = data
        self.mean = np.mean(data)
    """
    returns n random samples
    """
    def choice(self, n):
        return random.sample(self.data, n)
    """
    Samples the dataset n times of size s with alpha a,
    Checks howmany times of the samples mean lies 
     with intervals between the real mean.
    Plots the estimated means and their errorbars
    """
    def sample(self, n, s, a, plot=True):
        arr = []
        Y   = []
        err = []

        for i in range(0, s):
            samples = self.choice(n)
            c = self.errBound(samples, a)
            m = np.mean(samples)
            Y.append(m)
            err.append(c)
            arr.append( ( (m - c) <= self.mean) & ( self.mean <= (m + c)))
        # plot
        plt.errorbar(range(0, s), Y, yerr=err, fmt=None)
        plt.axhline(self.mean, color='r')

        return float(np.sum(arr))/len(arr)
    """
    Calculate the sample confidence bounds.
    returns (+c * s) / (sqrt(n)) where s is the unbiased std of samples.
    """
    def errBound(self, samples, a):
        n = len(samples)
        s = np.std(samples, ddof=1)
        c = stats.t.interval(a, n - 1)
        bounds = (c[1] * s) / (n**(1./2.))
    
        return bounds
    """
    Plot the data
    """
    def plot(self):
        plt.hist(self.data)

def logFile(fname):
    with open(fname) as f:
        arr = f.readlines()
    return np.array(arr).astype("float")

def main():
    data = logFile("tijden.log")
    conf = Confidence(data)
    print conf.sample(50, 100, 0.80)
    plt.show()
    
    print "real mean %s" % conf.mean

if __name__ == '__main__':
    main()