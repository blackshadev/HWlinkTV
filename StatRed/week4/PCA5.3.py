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
    d, U = np.linalg.eigh(M)
    si = np.argsort(d)[-1::-1]
    d = d[si]
    U = U[:,si]
    return (d, U)

""" Plots the max n eigenvalues their vectors as image """
def showMaxN(d, U, mu, n):
    max_idx = d.argsort()[-n:]
    
    pl.figure()
    count = 1
    for i in max_idx:
        pl.subplot(2,3,count)
        Y = np.reshape(U[:,i], (625, 1)) - mu
        pl.imshow(
            np.reshape(Y, (25,25)), 
            cmap=pl.cm.gray)
        count += 1
    pl.show()

def plotScree(Y, name=None):
    pl.bar(range(Y.size), Y)
    if name != None:
        pl.savefig(name)
    elif name != False:
        pl.show()

"""
    Reconstruct a sample of a on given position in k dimensions of U
    U eigenvectors of the covarience matrix of a
    mu the mean of a 
"""
def reconstructImage(U, mu, a, pos, k):
    mu = mu.flatten()

    # Sample to describe (25,25) image on given position
    im = a[pos[0]: (pos[0] + 25), pos[1]: (pos[1] + 25)] 
    X = im.flatten()

    print "Constructing Y, which is X in terms of U in %d dimensions" % k
    # Describe x in a space constructed by k dimensions of U
    X = X - mu # place center of samples to (0, 0)
    Uk = U[:,:k] # k dimensions of U
    Y = np.dot( Uk.transpose(), X) # yzm is x in Uk coordinate system in k dimensions

    print "Reconstructing X with Y"
    # Reconstruct x with yzm
    Xk = np.dot(Uk, Y) + mu
    imk = Xk.reshape(25, 25)

    # Plot images
    pl.subplot(121)
    pl.title("Original")
    pl.imshow(im, cmap='gray')
    pl.subplot(122)
    pl.title("Reconstructed")
    pl.imshow(imk, cmap='gray')
    pl.show()

""" Calculate with howmany elements (k) contains t percent of the total values """
def optimal_k(eigv, t=0.99):
    stop = t * np.sum(eigv)
    rSum = 0

    for i in range(0, eigv.size):
        if np.sum(eigv[0:i]) > stop:
            return i
    return -1

def main():
    print "Reading image"
    a = pl.imread("trui.png")

    print "Slicing image"
    X = np.array(
        [np.array(a[x:x+25,y:y+25]).flatten() 
            for x in range(0, a.shape[0] - 24, 4)
            for y in range(0, a.shape[1] - 24, 4)
        ]
        )

    print "Size of sample matrix: %s" %str(X.shape)
    print "Calculating covarience matrix"
    cov, mu = covMatrix(X)
    print "Calculating eigenvalues"
    d, U = sortedeig(cov)

    plotScree(d)
    showMaxN(d, U, mu, 6)

    k = optimal_k(d)
    reconstructImage(U, mu, a, (100, 100), k)
    reconstructImage(U, mu, a, (100, 100), k*2)


if __name__ == '__main__':
    main()