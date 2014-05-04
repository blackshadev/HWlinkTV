""" StatRed: Week 4 Opdr 5.3 
" 
" Authors: Tessa Klunder & Vincent Hagen
" Date   : 4-5-2014
"
" Plots multivariant normal distributed values for a given mu and sigma.
" It then estimates the values of the mean and the covariance. 
"
"""

import pylab as pl
import numpy as np

# Calculate the covariance matrix, with X being a 'slice' of the image. We  use 
# the formula from Exercise 5.1 to calculate the matrix.
def covMatrix(X):
    n = X.shape[0]

    done = 0
    # 'm' will be the estimator for the mean
    m = np.zeros((X.shape[1], 1))
    kwadSum = np.zeros((X.shape[1], X.shape[1]))
    print np.dot(m, np.transpose(m)).shape

    for i in range(X.shape[0]):
        x = np.array(X[i,:]).reshape((X.shape[1], 1))
        m += x
        kwadSum += np.dot(x, np.transpose(x))
        # Print status of calculation
        if float(i) / X.shape[0] > done / 10.:
            done += 1
            print "Cov Matrix (%s%%)" % str(int(done * 10))
    
    # Calculate the actual m by dividing it by n
    m /= n
    # Part of formula: Sum - (n * m.m^T)
    u = kwadSum - (n * np.dot(m, np.transpose(m)))
    return u / (n - 1) #Includes last step of formula

# Plots the six largest eigenvectors as images.
def showMaxN(eigv, eigb, n):
    max_idx = eigv.argsort()[-n:]
    
    pl.figure()
    count = 1
    for i in max_idx:
        pl.subplot(2,3,count)
        pl.imshow(
            np.reshape(eigb[:,i], (25,25)), 
            cmap=pl.cm.gray)
        count += 1
    pl.show()

# Plots the Scree diagram that shows all the eigenvalues from high to low.
def plotScree(Y):
    pl.figure()
    pl.bar(range(Y.size), sorted(Y, reverse=True))
    pl.show()

def main():
    print "Reading image"
    a = pl.imread("trui.png")

    print "Slicing image"
    X = np.array(
        [np.array(a[x:x+25,y:y+25]).flatten() 
            for x in range(0, a.shape[0] - 24, 1)
            for y in range(0, a.shape[1] - 24, 1)
        ]
        )

    print "Size of sample matrix: %s" %str(X.shape)
    print "Calculating covariance matrix"
    cov = covMatrix(X)
    print "Calculating eigenvalues"
    eigv, eigb = np.linalg.eigh(cov)

    plotScree(eigv)
    showMaxN(eigv, eigb, 6)
    

if __name__ == '__main__':
    main()