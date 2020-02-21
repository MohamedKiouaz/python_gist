import numpy as np
import scipy as sp

np.set_printoptions(suppress=True)

number_of_players = 3000
number_of_games = 10
k = 100

ratings = np.random.normal(1500, 1000, number_of_players)
true_rank = np.random.normal(1500, 1000, number_of_players)

def compare_elo(p1, p2):
    return 1/(1 + 10**((p2 - p1) / 400.0 ))

for l in range(2000):
    for i in range(number_of_players):
        for j in range(i+1, number_of_players):
            score1 = true_rank[i] > true_rank[j]
            score2 = 1 - score1
            expected1 = compare_elo(ratings[i], ratings[j])
            expected2 = compare_elo(ratings[j], ratings[i])
            ratings[i] = ratings[i] + k * (score1 - expected1)
            ratings[j] = ratings[j] + k * (score2 - expected2)
    
    print(l, np.abs(ratings.argsort() - true_rank.argsort()).mean(dtype = int))

    k = max(k * .9, 20)
    #if l % 10 == 0:
    #    for i in range(100):
    #        print("{:2f}/{:2f} {}/{}".format(float(ratings[i]), float(true_rank[i]), ratings.argsort()[i], true_rank.argsort()[i]))
