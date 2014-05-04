import pylab as pl
import numpy as np

def covMatrix(X):
    n = X.shape[0]

    done = 0
    m = np.zeros((X.shape[1], 1))
    kwadSum = np.zeros((X.shape[1], X.shape[1]))
    print np.dot(m, np.transpose(m)).shape

    for i in range(X.shape[0]):
        x = np.array(X[i,:]).reshape((X.shape[1], 1))
        m += x
        kwadSum += np.dot(x, np.transpose(x))
        if float(i) / X.shape[0] > done / 10.:
            done += 1
            print "Cov Matrix (%s%%)" % str(int(done * 10))
            
    m /= n
    u = kwadSum - (n * np.dot(m, np.transpose(m)))
    return u / (n - 1)

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

def plotScree(Y):
    pl.figure()
    pl.bar(range(Y.size), sorted(Y, reverse=True))
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
    cov = covMatrix(X)
    print "Calculating eigenvalues"
    eigv, eigb = np.linalg.eigh(cov)

    plotScree(eigv)
    showMaxN(eigv, eigb, 6)
    

if __name__ == '__main__':
    main()