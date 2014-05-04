""" StatRed: Week 3 Opdr 2 
" 
" Authors: Tessa Klunder & Vincent Hagen
" Date   : 19-4-2014
"
" Plots random values using the numpy random fn and an old IBM random fn
" Cmd Arguments:
"  1. amount of random values to use
"""

import random
import numpy as np
import sys
import time
import matplotlib.pyplot as plt

ibm_x = time.time()

ibm_m = 2 ** 31

n = 100

# Numpy random plot
def rndPlot():
    random.seed()
    X = np.random.rand(1, n)
    Y = np.random.rand(1, n)
    plt.title("Numpy rand")
    plt.scatter(X, Y)

# old IBM random function 
def ibmRnd():
    global ibm_x, ibm_m
    m = 2**31
    x = (ibm_x * (2**16 + 3) ) % ibm_m
    ibm_x = x
    return x / ibm_m

# IBM random plot
def ibmPlot():
    X = [ibmRnd() for i in range(0, n)]
    Y = [ibmRnd() for i in range(0, n)]
    plt.title("IBM RND")
    plt.scatter(X, Y)

# Both plots next to each other
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