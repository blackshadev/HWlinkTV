""" StatRed: Week 5 Opdr 4.4 
" 
" Authors: Tessa Klunder & Vincent Hagen
" Date   : 14-5-2014
"
" Implements the Minimum Error Classifier
"
"""

import numpy as np
import math
import matplotlib.pylab as pl
from collections import Counter

class MAP:
    def __init__(self, X, c):
        # Test set
        self.X = X
        self.c = list(c)

        # Classes grouped
        self.classes = list(set(self.c))
        
        self.mean = []
        self.cov = []
        
        self.learn()
    """
    Learns the dataset by calculating the mean and covarience matrix of the 
     data grouped by class
    """
    def learn(self):

        self.mean = ([np.mean(self.ofClass(i), axis=0) for i in self.classes])
        self.cov = ([np.cov(np.transpose(self.ofClass(i))) for i in self.classes])
    """
    Returns a list of all items in the test set of the given class
    """
    def ofClass(self, c):
        return np.array([self.X[:,i] for i in range(0, len(self.c)) if self.c[i] == c])
    """
    Classifies a given X with the learned set
    """
    def test(self, X):
        results = []

        for i in range(len(self.classes)):
            mu = self.mean[i]
            si = self.cov[i]
            xmz = np.transpose(X - mu);
            # (-1/2) * (x - mu)^T Sigma^-1 (x - mu)
            upper = np.exp(-0.5 * np.dot(np.transpose(xmz), \
                np.dot( np.linalg.inv(si), xmz)))
            # |Sigma| ^(-1/2) *  (2 * pi)^(n/2) 
            lower = np.linalg.det(si) ** (-0.5) * (2 * math.pi) ** (si.shape[0] / 2)
            results.append(upper / lower)
        return self.classes[np.argmax(results)]

# from pdf handout_6_Classification
def cnvt(s):
    tab = {'Iris-setosa':1.0, 'Iris-versicolor':2.0, 'Iris-virginica':3.0}
    if tab.has_key(s):
        return tab[s]
    else:
        return -1.0

XC = np.loadtxt('data.csv', delimiter=',', dtype=float, converters={4: cnvt})

ind = np.arange(150) # indices into the dataset

ind = np.random.permutation(ind) # random permutation
L = ind[0:90] # learning set indices
T = ind[90:] # test set indices

# Learn the learn set in the minimum error classifier
X = np.transpose(XC[L,0:4])
minErr = MAP(X, XC[L,-1])

# from pdf handout_6_Classification
c = np.zeros(len(T))
for i in np.arange(len(T)):
    c[i] = minErr.test(XC[T[i],0:4])

# Confusion Matrix
CM = np.zeros((3,3))
for i in range(3):
    for j in range(3):
        CM[i,j] = sum( np.logical_and(XC[T,4] == (i + 1), c == (j + 1)) )

print(CM)

pl.figure(1)
color = np.array( [[1,0,0],[0,1,0],[0,0,1]] )
for i in range(4):
    for j in range(4):
        pl.subplot(4,4,4*i+j+1)
        if i==j:
            continue
        pl.scatter( XC[T,i], XC[T,j], s=100, marker='s',
            edgecolor=color[XC[T,4].astype(int)-1],
            facecolor=[1,1,1]*len(T))
        pl.scatter( XC[T,i], XC[T,j], s=30, marker='+',
            edgecolor=color[c.astype(int)-1])

pl.savefig("minerrtest.png")