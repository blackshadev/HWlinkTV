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
    pl.bar(range(Y.size), Y)
    if name != None:
        pl.savefig(name)
    elif name != False:
        pl.show()

def reconstructImage(eigb, mu, a, pos):
    X = a[:,42]
    print X.shape, mu.shape
    X = X - mu

    yzm = np.dot(np.transpose(eigb), X)
    yzm = yzm[:-1]
    U = eigb[:,:-1]
    print U.shape
    xzm_k = np.dot(U, yzm)

    x_k = xzm_k + mu
    pl.imshow(x_k, cmap=pl.cm.gray)
    pl.show()


def main():
    print "Reading image"
    a = pl.imread("trui.png")
    # pl.figure(1)

    # pl.subplot(1,2,1)
    # pl.imshow(a,cmap=pl.cm.gray)
    # d = a[100:126,100:126]
    # pl.subplot(1,2,2)
    # pl.imshow(d,cmap=pl.cm.gray)
    # pl.show()

    print "Slicing image"
    X = np.array(
        [np.array(a[x:x+25,y:y+25]).flatten() 
            for x in range(0, a.shape[0] - 24, 1)
            for y in range(0, a.shape[1] - 24, 1)
        ]
        )

    print "Size of sample matrix: %s" %str(X.shape)
    print "Calculating covarience matrix"
    cov, mu = covMatrix(X)
    print "Calculating eigenvalues"
    eigv, eigb = sortedeig(cov)

    print eigv

    plotScree(eigv)
    showMaxN(eigv, eigb, mu, 6)
    reconstructImage(eigb, mu, a, (100,100))

if __name__ == '__main__':
    main()