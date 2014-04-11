import scipy
import scipy.stats as stats
import numpy as np
import csv
import math


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
    def __init__(self, arr, t):
        # we assume that in arr, we predict the first row, ad te rest is data
        self.arr = arr
        # t is the apprioti change of female divided by that of a male
        self.t = t
    def learn(self):

        self.normals = []

        # all indices used in the learning process
        idx = range(0, len(self.arr))
        items = np.array([self.arr[i] for i in idx])

        # Mask for all males
        mask = items[:,0] < 1

        # calculate one patch of normals (for males)
        means = np.mean(items[mask][:,1:], axis=0)
        stds  = np.std(items[mask][:,1:], axis=0)

        self.normals.append([stats.norm(loc=means[i], scale=stds[i]) \
              for i in range(0, len(means))])

        # inverse mask. Mark for the ladies
        mask = [not i for i in mask]

        # Calc mean and stdev for females
        means = np.mean(items[mask][:,1:], axis=0)
        stds  = np.std(items[mask][:,1:], axis=0)

        self.normals.append([stats.norm(loc=means[i], scale=stds[i]) \
              for i in range(0, len(means))])

    def test(self, dat):
        chance = [];

        if len(dat) != len(self.normals[0]):
            print "Incompatible data, need to be of length " + len(self.normals[0])
            return

        # log chance to be a male, using the sum of logpdf for males
        chance.append(sum([self.normals[0][i].logpdf(dat[i]) for i in range(len(dat))]))
        # log chance to be a male, using the sum of logpdf for females
        chance.append(sum([self.normals[1][i].logpdf(dat[i]) for i in range(len(dat))]))

        print chance

        t = chance[0] - chance[1]

        return t > math.log(self.t);




def main():
    arr = readCsv("biometrie2014.csv", 5)
    nb = NBClassifier(arr, 1.)
    nb.learn()
    print nb.test([55, 170, 42]) # ik
    print nb.test([98, 189, 44]) # man
    print nb.test([63, 173, 41]) # vrouw



if __name__ == '__main__':
    main()