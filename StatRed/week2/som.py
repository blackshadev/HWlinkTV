"""
StatRed Inf 2 - 2014

Students: Tessa Klunder, Vincent Hagen

Week 1 Assignment 2.d
"""

from math import factorial

# Function for binomial coefficient
def binomial_coefficient(n, k):
    return factorial(n) // factorial(k) // factorial(n-k)

tot = 0    #total probability per test (always 1)
n   = 20   #number of throws per test
p   = 0.8  #chosen probability that 'tails' is thrown
l   = 100  #extra: largest number of throws

#extra: a for loop to test for multiple values for n, stepsize of 10
for n in range(10, l, 10):
    for k in range(0, n+1):
        tot +=  binomial_coefficient(n, k) * p**k * (1-p)**(n-k)
    
    print "n is {}: {}".format(n, tot)
    
    #reset total for next test with larger n
    tot = 0 



