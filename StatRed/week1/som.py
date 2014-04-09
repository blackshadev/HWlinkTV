from math import factorial

# Function for binomial coefficient
def binomial_coefficient(n, k):
    return factorial(n) // factorial(k) // factorial(n-k)

tot = 0    #total probability
n   = 20   #number of throws
g   = 100  #largest number of throws
p   = 0.8  #probability that 'tails' is thrown

for n in range(10, g, 10):
    for k in range(0, n+1):
        tot +=  binomial_coefficient(n, k) * p**k * (1-p)**(n-k)
    
    print "n is {}: {}".format(n, tot)
    tot = 0



