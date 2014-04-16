import random
import numpy as np
import sys
import time
import matplotlib.pyplot as plt

ibm_x = time.time()

ibm_m = 2 ** 31

n = 100

def rndPlot():
    random.seed()
    X = np.random.rand(1, n)
    Y = np.random.rand(1, n)
    plt.title("Numpy rand")
    plt.scatter(X, Y)
 
def ibmRnd():
    global ibm_x, ibm_m
    m = 2**31
    x = (ibm_x * (2**16 + 3) ) % ibm_m
    ibm_x = x
    return x / ibm_m

def ibmPlot():
    X = [ibmRnd() for i in range(0, n)]
    Y = [ibmRnd() for i in range(0, n)]
    plt.title("IBM RND")
    plt.scatter(X, Y)


def compareIbmRand():
    plt.figure()
    plt.subplot(121)
    rndPlot()
    plt.subplot(122)
    ibmPlot()


def main():
    global n
    if len(sys.argv) > 1:
        n = int(sys.argv[1])
    compareIbmRand()
    plt.show()

if __name__ == '__main__':
    main()