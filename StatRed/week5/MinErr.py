import numpy as np
import scipy.stats as stats
import matplotlib.pylab as pl

def cnvt(s):
    tab = {'Iris-setosa':1.0, 'Iris-versicolor':2.0, 'Iris-virginica':3.0}
    if tab.has_key(s):
        return tab[s]
    else:
        return -1.0

mu_1 = 4
mu_2 = 7

si_1 = 1
si_2 = 1.5

norm = stats.norm

X = np.arange(-5,15, step=0.1)

P_xc_1 = norm.pdf(X, loc=mu_1, scale=si_1) * 0.3
P_xc_2 = norm.pdf(X, loc=mu_2, scale=si_2) * 0.7
p_x = P_xc_1 + P_xc_2

pl.plot(X, P_xc_1, 'b-')
pl.plot(X, P_xc_2, 'r-')

pl.plot(X, P_xc_1 / p_x, 'b--')
pl.plot(X, P_xc_2 / p_x, 'r--')


pl.show()