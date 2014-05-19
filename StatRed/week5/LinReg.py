from pylab import linspace, randn, ones, vstack, plot, savefig, dot, norm, figure, show, clf, contour, colorbar
from scipy.optimize import minimize
import numpy as np

th1 = 2
th2 = .5
th = [th1, th2]
rndVar = 0.3


def fn(x, th):
	return th[0] * np.sin(th[1] * x)

x = linspace(0,10,100)
y = fn(x, th) + rndVar * np.random.randn(*x.shape)
X = vstack((ones(x.shape),x)).T


def J(th):
	return np.sum((y - fn(x, th))**2)

def Jac(th):
	dth1 = np.sum(2 * np.sin(x * th[1]) * (th[0] * np.sin(x * th[1]) - y))
	dth2 = np.sum(2 * x * th[0] * np.cos(x * th[1]) * (th[0] * np.sin(x * th[1]) - y))
	return np.array([dth1, dth2])

res = minimize(J, (3, .65), jac=Jac, method='CG')
print res

eth1, eth2 = res.x

t1a = linspace(0,4,100)
t2a = linspace(0,4,100)
Jim = np.array( [J((t1,t2)) for t1 in t1a for t2 in t2a] ).reshape(100,100)
figure(1); clf(); contour(t2a, t1a, Jim); colorbar()
savefig("Jplot.png")

clf()
figure(1)
plot(x, y, 'xb')
plot(x, fn(x, [eth1, eth2]), 'b')
plot(x, fn(x, th), 'g')
savefig('linregression.png')