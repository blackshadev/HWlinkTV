import pylab as pl
import numpy as np


""" Calculate the covarience matrix with the formula given
    In exercise 5.1 """ 
def covMatrix(X):
    n = X.shape[0]

    done = 0
    m = np.zeros((X.shape[1], 1))
    kwadSum = np.zeros((X.shape[1], X.shape[1]))

    for i in range(X.shape[0]):
        x = np.array(X[i,:]).reshape((X.shape[1], 1))
        m += x
        kwadSum += np.dot(x, np.transpose(x))
        if float(i) / X.shape[0] > done / 10.:
            print "Cov Matrix (%s%%)" % str(int(done * 10))
            done += 1
            
    m /= n
    u = kwadSum - (n * np.dot(m, np.transpose(m)))
    return (u / (n - 1), m)

""" Sort the eigenvectors based upon their eigenvalues (desc)
    Copied from pdf ~handout_5_PCA """
def sortedeig(M):
    d, U = np.linalg.eig(M)
    si = np.argsort(d)[-1::-1]
    d = d[si]
    U = U[:,si]
    return (d, U)

""" Plots the max n eigenvalues their vectors as image """
def showMaxN(eigv, eigb, mu, n):
    max_idx = eigv.argsort()[-n:]
    
    pl.figure()
    count = 1
    for i in max_idx:
        pl.subplot(2,3,count)
        Y = np.reshape(eigb[:,i], (625, 1)) - mu
        pl.imshow(
            np.reshape(Y, (25,25)), 
            cmap=pl.cm.gray)
        count += 1
    pl.show()

def plotScree(Y, name=None):
    pl.bar(range(Y.shape[0]), Y)
    if name != None and name != False:
        pl.savefig(name)
    elif name != False:
        pl.show()


def norm_cum(Y):
    return np.cumsum(Y) / np.sum(Y)

""" Calculate with howmany elements (k) contains t percent of the total values """
def optimal_k(eigv, t=0.99):
    stop = t * np.sum(eigv)
    rSum = 0

    for i in range(0, eigv.size):
        if np.sum(eigv[0:i]) > stop:
            return i
    return -1

""" Constructs a vector x which is a subset of X in terms of 
    eigenvectors U of covarience matrix of X, 
    mean of the whole dataset X,
     """
def constructSpectByU(x, U, mean, k):
    x = np.copy(x)
    x -= mean
    return np.dot(np.transpose(U), x)[:-k]

def reconstructSpect(Y, U, mean, k):
    _X = np.dot(U[:,:-k], Y)
    return _X + mean

def main():
    print "Loading data `natural400_700_5`"
    a = pl.loadtxt("natural400_700_5.asc")
    print "data has shape: %s" % str(a.shape)
    print "Calculating covarience" 
    a_cov, a_mu = covMatrix(a)
    print "Calculating eigenvalues"
    a_eigv, a_eigb = sortedeig(a_cov)

    print "Loading data `munsell380_800_1`"
    b = pl.loadtxt("munsell380_800_1.asc")
    b = np.reshape(b, (1269, 421))
    
    print "data has shape: %s" % str(b.shape)
    print "Calculating covarience" 
    b_cov, b_mu = covMatrix(b)
    print "Calculating eigenvalues"
    b_eigv, b_eigb = sortedeig(b_cov)

    print "Plotting Scree diagrams"
    pl.clf()
    pl.subplot(211)
    pl.title("Natural")
    plotScree(a_eigv, False)
    pl.subplot(212)
    pl.title("Munsell")
    plotScree(b_eigv, "Scree_Diagrams.png")
    
    print "Plotting cumulative scree Diagrams"
    pl.clf()
    pl.subplot(211)
    pl.title("Natural")
    plotScree(norm_cum(a_eigv), False)
    pl.subplot(212)
    pl.title("Munsell")
    plotScree(norm_cum(b_eigv), "Cum_Scree_Diagrams.png")

    nat_3_pca = np.sum(a_eigv[0:3]) / np.sum(a_eigv)
    mun_3_pca = np.sum(b_eigv[0:3]) / np.sum(b_eigv)

    print "First 3 components of Natural capture %s %%" % str(nat_3_pca * 100)
    print "First 3 components of Munsell capture %s %%" % str(mun_3_pca * 100)


    print "Finding K values to contain 99% of the spectrum"
    a_k = optimal_k(a_eigv)
    b_k = optimal_k(b_eigv)

    print "Natural k: %d, Munsell k: %d" % (a_k, b_k)

    x = np.transpose(a)[:,42]
    print "sample vector"
    print x

    print "Constructing vector by U"
    Y = constructSpectByU(x, a_eigb, np.mean(a, 0), a_k)

    print "Reconstructing spectrum"
    _x = reconstructSpect(Y, a_eigb, np.mean(a, 0), a_k)

    print "Reconstructed sample vector"
    print _x

    print "difference"
    print str(abs(x - _x))

if __name__ == '__main__':
    main()