import numpy as np
import matplotlib.pyplot as plt

def Simulation(initial):
    balance = initial
    fees = 0
    balance += 0.004
    while(balance > 0):
        fees += .25 * balance
        balance *= .25
        if(balance < 0.0001):
            balance = 0
    return fees

b = np.linspace(0.00001, 1, 250)
bb = [Simulation(k) for k in b]
plt.plot(bb-b)