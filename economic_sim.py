import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def activate(input_, genom):
    input_ = np.array(input_)
    hidden_ = np.tanh(np.dot(genom[0], input_) + genom[1])
    return np.tanh(np.dot(genom[2], hidden_) + genom[3])

class Player():
    def __init__(self, money, food, genom=None):
        self.name = ''.join(np.random.choice(list('ABCDEFGHIJKLMNOPQRSTUVWXYZ'), size=3))
        self.money = money
        self.food = food
        self.alive = True
        self.shares = 1
        self.choice = None
        self.genom = (
            genom
            if genom is not None
            else [np.random.rand(4, 4) for _ in range(2)]
        )

    def __str__(self):
        return f'{self.name}, food: {self.food:.2f}, shares: {self.shares:.2f}, money: {self.money:.2f}'
    
    def buy_food(self, food, food_price):
        self.money -= food_price
        self.food += food

    def invest(self, shares, money):
        self.money -= money
        self.shares += shares
    
    def divest(self, shares, money):
        self.money += money
        self.shares -= shares

    def eat(self):
        self.food -= 1
        if self.food < 0:
            self.alive = False

    def choose(self, food_price):
        inputs = [self.food, self.money, food_price, self.shares]
            
        if self.food < 50:
            if self.money > 10:
                self.choice = 'buy_food'
            elif self.shares > 0:
                self.choice = 'sell_shares'
            else:
                self.choice = 'work'
        elif self.money > 10:
                self.choice = 'invest'
        else:
            self.choice = 'work'
        if np.random.rand() < .1:
            np.random.choice(['sell_shares', 'invest', 'buy_food', 'work'])

    def work(self, money):
        self.money += money
    
    def get_dividends(self, money):
        self.money += money
    
class Zone():
    def __init__(self, n_players, ressources):
        self.ressources = 100 * n_players
        self.players = [Player(np.random.rand()*100, np.random.randint(10, 15)) for i in range(n_players)]
        self.jobs_money = n_players
        self.food_price = 1
        self.dividends = 0
        self.d = {}

    def state(self):
        players = [p for p in self.players if p.alive]
        self.d['alive'] = len(players)
        self.d['mean_money'] = np.mean([p.money for p  in self.players])
        self.d['mean_food'] = np.mean([p.food for p  in self.players])
        self.d['max_money'] = np.max([p.money for p  in self.players])
        self.d['max_food'] = np.max([p.food for p  in self.players])
        self.d['mean_shares'] = np.mean([p.shares for p  in self.players])
        self.d['max_shares'] = np.max([p.shares for p  in self.players])
        self.d['food_price'] = self.food_price
        self.d['exchange_money'] = self.exchange_money
        return self.d

    def done(self):
        return sum(p.alive for p in self.players) <= 1 

    def eat(self):
        players = [p for p in self.players if p.alive]
        dead = 0
        for player in players:
            player.eat()
            dead += not player.alive
        if dead > 0:
            print(f'{dead} died of starvation')

    def choice(self):
        for player in self.players:
            player.choose(self.food_price)
        
        choices = [p.choice for p in self.players if p.alive]
        for choice in ['work', 'invest', 'sell_shares', 'buy_food']:
            self.d['choice_' + choice] = choices.count(choice)

    def tax(self):
        players = [p for p in self.players if p.alive]
        tax = 0
        m2 = sum(p.money for p in players)

        for player in players:
            if player.money > 10:
                amount = (player.money - 10) * .3
                player.money -= amount
                tax += amount
        self.d['global_tax'] = tax
        self.d['destroyed_money'] = 0
        if m2/len(players) > 20:
            self.d['destroyed_money'] = tax * .17
            tax *= .83

        for player in players:
            player.money += tax / len(players)

    def simulate(self):
        self.eat()
        self.choice()
        self.execute()
        self.tax()

    def execute(self):
        self.exchange_money = 0
        done = False
        players = [p for p in self.players if p.alive and p.choice == 'buy_food']
        while not done and self.ressources > 0:
            buy_side = sum(p.money / 2 for p in players)
            food_price = buy_side / self.ressources
            if buy_side == 0:
                break
            if all(p.money / 2 >= food_price for p in players):
                self.exchange_money += buy_side
                for player in players:
                    player.buy_food(player.money / 2 / buy_side * self.ressources, player.money)
                self.food_price = food_price
                self.ressources = 0
                done = True
            else:
                players = [p for p in self.players if p.alive and p.choice == 'buy_food' and p.money / 2 >= food_price]

        investors = [p for p in self.players if p.alive and p.choice == 'invest' and p.money > 0]
        divestors = [p for p in self.players if p.alive and p.choice == 'sell_shares' and p.shares > 0]
        done = False
        if not investors or not divestors:
            done = True

        while not done:
            sell_side = sum(p.shares for p in divestors)
            buy_side = sum(p.money / 2 for p in investors)
            self.d['n_investors'] = len(investors)
            self.d['n_divestors'] = len(divestors)
            if buy_side == 0 or sell_side == 0:
                break
            self.exchange_money += buy_side
            for player in investors:
                player.invest(sell_side * player.money / 2 / buy_side, player.money / 2)
            for player in divestors:
                player.divest(player.shares, player.shares / sell_side * buy_side)
            done = True

        workers = [p for p in self.players if p.alive and p.choice == 'work']
        self.d['n_workers'] = len(workers)
        if workers:
            amount = self.jobs_money / len(workers)
            #print(f'{len(workers)} workers earned {amount:.2f}')
            for worker in workers:
                worker.work(amount)
                self.ressources += 1.5
                self.dividends += .2 * amount

        total_shares = sum(p.shares for p in self.players)
        for player in [player for player in self.players if player.shares > 0]:
            player.get_dividends(player.shares / total_shares * self.dividends)
        self.dividends = 0
        

class Game():
    def __init__(self, n_zones, n_players):
        self.zones = [Zone(n_players) for _ in range(n_zones)]
        self.public_market = 10000
    
    def simulate(self):
        for zone in self.zones:
            zone.simulate()
    

def main():
    z = Zone(2000, 5)
    states = []
    i = 0 
    while not z.done():
        i += 1
        z.simulate()
        states.append(z.state().copy())
        if i > 100:
            break
    
    states_df = pd.DataFrame(states)
    print(states_df.columns)

    fig = make_subplots(rows=3, cols=2,
    subplot_titles=('choices', 'distribution', 'tax', 'shares', 'money', 'food'))

    for col in ['choice_work', 'choice_invest', 'choice_buy_food', 'choice_sell_shares']:
        fig.add_trace(go.Scatter(x=states_df.index, y=states_df[col], name=col), row=1, col=1)
    for col in ['n_workers', 'n_investors', 'n_divestors']:
        fig.add_trace(go.Scatter(x=states_df.index, y=states_df[col], name=col), row=2, col=1)
    for col in ['global_tax', 'destroyed_money']:
        fig.add_trace(go.Scatter(x=states_df.index, y=states_df[col], name=col), row=3, col=1)
    for col in ['max_shares', 'mean_shares']:
        fig.add_trace(go.Scatter(x=states_df.index, y=states_df[col], name=col), row=1, col=2)
    for col in ['max_money', 'mean_money']:
        fig.add_trace(go.Scatter(x=states_df.index, y=states_df[col], name=col), row=2, col=2)
    for col in ['max_food', 'mean_food']:
        fig.add_trace(go.Scatter(x=states_df.index, y=states_df[col], name=col), row=3, col=2)
    fig.show()
    return

if __name__ == '__main__':
    main()