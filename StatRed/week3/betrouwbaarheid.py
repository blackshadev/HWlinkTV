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
    """
    def sample(self, n, s, a):
        arr = []

        for i in range(0, s):
            samples = self.choice(n)
            c = self.calcBounds(samples, a)
            m = np.mean(samples)
            arr.append( ( (m - c) <= self.mean) & ( self.mean <= (m + c)))
        print float(np.sum(arr))/len(arr)
    """
    Calculate the sample confidence bounds.
    returns (+c * s) / (sqrt(n)) where s is the unbiased std of samples.
    """
    def calcBounds(self, samples, a):
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
        plt.show()

def logFile(fname):
    with open(fname) as f:
        arr = f.readlines()
    return np.array(arr).astype("float")

def main():
    data = logFile("tijden.log")
    conf = Confidence(data)
    conf.sample(50, 100, 0.90)
    
    print "real mean %s" % conf.mean

if __name__ == '__main__':
    main()