""" StatRed: Naive Bayes Classifier 
" 
" Authors: Tessa Klunder & Vincent Hagen
" Date   : 12-4-2014
"
" Implements a naive bayes classifier. 
" It reads biometrie2014.csv, and can predict the sex of someone by body length, 
" shoe size and weight.
"  ( Apparently Vincent is female... Well that's new! )
"""

import scipy
import scipy.stats as stats
import numpy as np
import csv
import math
import matplotlib.pyplot as plt

# Helper function, returns a subset of items where mask[i] is True
def getRows(items, mask):
    return np.array([items[i] for i in range(len(mask)) if mask[i]])

# Read in csv, translates M to 0 and F to 1, returns as numpy array
def readCsv(fname, skip):
    a = []
    csvReader = csv.reader(open(fname, 'rb'))
    for i in range(0, skip):
        csvReader.next()
    for row in csvReader:
        row[0] = 0 if row[0] == "M " else 1
        a.append(row)
    return np.array(a).astype('float')

class NBClassifier:
    """
    In this case Males will be identified by 0, females by 1
    """
    __dict__ = ["means", "stds", "arr", "t", "labels"]
    def __init__(self, arr, t, labels):
        # we assume that in arr, we predict the first row and the rest is data
        self.arr = arr
        # t is the a priori chance of female divided by that of a male
        self.t = t
        self.means = []
        self.stds = []
        self.labels = labels
    """
    Learns a subset of the given array. If idx is not filled it will use the
    whole array. Idx is an array with indices of the data array (arr)
    """
    def learn(self, idx=None):
        self.normals = []

        # all indices used in the learning process
        if idx == None:
            idx = range(0, len(self.arr))

        items = np.array([self.arr[i] for i in idx])

        # mask for all males
        mask = np.ma.array(items[:,0] < 1)
        subs = getRows(items, mask)

        # calculate one patch of normals (for males)
        self.means.append(np.mean(subs[:,1:], axis=0))
        self.stds.append(np.std(subs[:,1:], axis=0))

        self.normals.append([stats.norm(loc=self.means[0][i], \
            scale=self.stds[0][i]) for i in range(0, len(self.means[0]))])

        # inverse mask. Mark for the ladies
        mask = [not i for i in mask]
        subs = getRows(items, mask)

        # Calc mean and stdev for females
        self.means.append(np.mean(subs[:,1:], axis=0))
        self.stds.append(np.std(subs[:,1:], axis=0))

        self.normals.append([stats.norm(loc=self.means[1][i], \
            scale=self.stds[1][i]) for i in range(0, len(self.means[1]))])
    """
    Tests a case given in dat.
    It will return True or False whether it is a match or not.
    (In our case True = Male, False = Female)
    """
    def test(self, dat):
        chance = [];

        if len(dat) != len(self.normals[0]):
            print "Incompatible data, need to be of length " + len(self.normals[0])
            return

        # log chance to be a male, using the sum of logpdf for males
        chance.append(sum([self.normals[0][i].logpdf(dat[i]) for i in range(len(dat))]))
        # log chance to be a male, using the sum of logpdf for females
        chance.append(sum([self.normals[1][i].logpdf(dat[i]) for i in range(len(dat))]))

        t = chance[0] - chance[1]

        return t > math.log(self.t);
    """
    Repeatedly learns with a set -1 record, and tests that record. 
    It will count the amount of hits and misses in  a confusionMatrix
    """
    def confusionMatrix(self):
        matrix = np.zeros((2,2))
        for i in range(0, len(self.arr)):
            # Learn set by index
            idx = range(0, len(self.arr))
            del idx[i]
            self.learn(idx)

            actual = self.arr[i];
            res = 0 if self.test(actual[1:]) else 1
            matrix[actual[0], res] += 1
        return matrix
    """
    Plots all normal pdf functions
    """
    def plot(self):
        for i in range(0, len(self.normals[0])):
            loc = min([self.means[0][i], self.normals[1][i]])
            std = max([5 * self.stds[0][i], 5 * self.stds[1][i]])
            x = np.linspace(loc - std, loc + std, 100 * std)
            plt.figure()
            plt.title(self.labels[i+1])
            plt.plot(x, self.normals[0][i].pdf(x), label="Mannen")
            plt.plot(x, self.normals[1][i].pdf(x), label="Vrouwen")
            plt.legend()
            plt.show()


def main():
    arr = readCsv("biometrie2014.csv", 5)
    nb = NBClassifier(arr, 1., ["Geslacht", "Gewicht", "Lengte", "Schoenmaat"])
    # nb.learn()
    # nb.plot()
    print nb.confusionMatrix()

if __name__ == '__main__':
    main()