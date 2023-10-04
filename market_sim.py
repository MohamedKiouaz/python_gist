import numpy as np
from loguru import logger as log


class Human:
    def __init__(self):
        self.money = 0
        self.age = 0
        self.alive = True
        self.id = 0

    def __str__(self):
        return f"Human: {self.id} {self.money:.0f}€ {self.age:.1f} {self.alive}"        

    def end_turn(self):
        if self.alive is False:
            return
        self.age += 1/12
        self.earn(-1000)

    def earn(self, amount):
        self.money += amount
        if self.money < 0:
            self.alive = False

class Investor(Human):
    def __init__(self):
        super().__init__()
        self.money = 1000000
        self.age = 25
        self.investments = []

    def __str__(self):
        return f"Investor: {self.id} {self.money:.0f}€ {self.age:.1f} {self.alive} {len(self.investments)}"

    def offer_salary(self, trader):
        return 0.001 * self.money

    def hire_trader(self, trader):
        trader.ceo = self
        trader.salary = self.offer_salary(trader)

    def invest(self, project):
        self.money -= project.amount
        self.investments.append(project)
        project.share_holder = self

class Trader(Human):
    def __init__(self):
        super().__init__()
        self.money = 50000
        self.age = 25
        self.ceo = None
        self.salary = 0
        self.projects = []
        self.projects_estimator = ProjectEstimator()
        self.projects_estimator.randomize()
        self.trade_history = []

    def __str__(self):
        return f"Trader: {self.id} {self.money:.0f}€ {self.age:.1f} {self.alive} I{self.ceo.id if self.ceo else None} {self.salary:.0f}€ {len(self.projects)}"

    def estimate(self, project):
        return self.projects_estimator.estimate(project)

    def choose_project(self):
        estimates = [self.estimate(project) for project in self.projects]
        estimates = [k for k in estimates if k.std < .2]
        estimates = [k for k in estimates if k.mean > 1 and k.project.amount < self.ceo.money]
        estimates.sort(key=lambda x: x.mean)

        return estimates[-1] if estimates else None
    
    def answer_offer(self, salary):
        return salary > self.salary
    
    def end_turn(self):
        super().end_turn()
        if self.ceo is not None and not self.ceo.alive:
            self.ceo = None

class ProjectEstimator:
    def __init__(self):
        self.mean_bias = 0
        self.std_bias = 0
        self.skew_bias = 0
        self.amount_std = 0
        self.mean_std = 0
        self.std_std = 0
        self.skew_std = 0

    def __str__(self):
        return f"ProjectEstimator: {self.mean_bias:.2f} {self.std_bias:.2f} {self.skew_bias:.2f} {self.amount_std:.2f} {self.mean_std:.2f} {self.std_std:.2f} {self.skew_std:.2f}"

    def randomize(self):
        self.mean_bias = (np.random.randn() - .5) * .2
        self.std_bias = (np.random.randn() - .5) * .2
        self.skew_bias = (np.random.randn() - .5) * .2
        self.mean_std = np.random.rand() * .2
        self.std_std = np.random.rand() * .2
        self.skew_std = np.random.rand() * .2

    def estimate(self, project):
        mean = project.mean + self.mean_bias + np.random.randn() * self.mean_std
        std = project.std + self.std_bias + np.random.randn() * self.std_std
        skew = project.skew + self.skew_bias + np.random.randn() * self.skew_std
        return ProjectEstimate(project, mean, std, skew)
    

class ProjectEstimate:
    def __init__(self, project, mean, std, skew):
        self.project = project
        self.mean = mean
        self.std = std
        self.skew = skew

class Project:
    def __init__(self):
        self.amount = 0
        self.mean = 0
        self.std = 0
        self.skew = 0
        self.realization = 0
        self.maturity = 0
        self.share_holder = None

    def __str__(self):
        return f"Project: {self.amount:.0f}€ * {self.mean:.2f}+{self.std:.2f} {self.skew:.2f} {self.realization:.2f} {self.maturity} {self.share_holder.id if self.share_holder else None}"

    def randomize(self):
        self.amount = np.random.randint(1000, 100000)
        self.mean = np.random.rand() + .5
        self.std = np.random.rand() * .6
        self.skew = np.random.randint(-100, 100)
        self.maturity = np.random.randint(1, 40)

    def mature(self):
        if self.maturity == 0 or self.share_holder is None:
            return
        
        self.maturity -= 1
        if self.maturity == 0:
            self.realize()
            self.share_holder.earn(self.amount * self.realization)
            return self.amount * self.realization
            #log.info(f"Project {self} realized {self.realization}")

    def realize(self):
        self.realization = np.random.normal(self.mean, self.std)

class Market:
    def __init__(self):
        self.projects = []
        self.projects_graveyard = []
        self.investors = []
        self.investors_graveyard = []
        self.traders = []
        self.traders_graveyard = []
        self.matured = []

    def add_projects(self, N):
        for _ in range(N):
            self.projects.append(Project())

        for project in self.projects:
            project.randomize()

    def add_investors(self, N):
        for _ in range(N):
            self.investors.append(Investor())
            self.investors[-1].id = len(self.investors) + len(self.traders)

    def add_traders(self, N):
        for _ in range(N):
            self.traders.append(Trader())
            self.traders[-1].id = len(self.investors) + len(self.traders)

    def hire_traders(self):
        N = len(self.investors) + len(self.traders)

        for _ in range(5 * N):
            investors = [investor for investor in self.investors if investor.alive]
            traders = [trader for trader in self.traders if trader.alive]
            if not investors or not traders:
                break
            investor = np.random.choice(investors)
            trader = np.random.choice(traders)
            salary = investor.offer_salary(trader)
            if trader.answer_offer(salary):
                investor.hire_trader(trader)

    def estimate_projects(self):
        for trader in self.traders:
            if trader.ceo is None:
                continue

            projects = [project for project in self.projects if project.maturity > 0 and project.share_holder is None]
            projects = np.random.choice(self.projects, 10)
            trader.projects = projects
            project_estimate = trader.choose_project()
        
            if project_estimate is None:
                continue
            shareholder = trader.ceo
            shareholder.invest(project_estimate.project) 

    def mature_projects(self):
        matured = 0
        for project in self.projects:
            val = project.mature()
            if val is not None:
                matured += val
        self.matured += [matured]

    def pay_salaries(self):
        for trader in self.traders:
            employer = trader.ceo
            if employer is None:
                continue
            employer.earn(-trader.salary)
            trader.earn(trader.salary)

    def end_turn(self):
        for investor in self.investors:
            investor.end_turn()

        for trader in self.traders:
            trader.end_turn()

        # move dead investors to graveyard
        self.investors_graveyard += [investor for investor in self.investors if not investor.alive]
        self.investors = [investor for investor in self.investors if investor.alive]

        # move dead traders to graveyard
        self.traders_graveyard += [trader for trader in self.traders if not trader.alive]
        self.traders = [trader for trader in self.traders if trader.alive]

        # move dead projects to graveyard
        self.projects_graveyard += [project for project in self.projects if project.maturity == 0]
        self.projects = [project for project in self.projects if project.maturity > 0]
        self.projects = self.projects[int(len(self.projects)*.01):]
        
    def log(self):
        # log % of projects realized
        realized = [project for project in self.projects if project.realization > 0]
        log.info(f"Projects realized: {len(realized)}/{len(self.projects + self.projects_graveyard)}")
        running = [project for project in self.projects if project.share_holder is not None]
        log.info(f"Projects running: {len(running)}/{len(self.projects)}")
        
        # log last 5 maturations
        log.info(f"Last 5 maturations: {', '.join(f'{matured:.0f}€' for matured in self.matured[-5:])}")

        # log % of investors alive
        log.info(f"Investors alive: {len(self.investors)}/{len(self.investors + self.investors_graveyard)}")
        log.info(f"Average money of alive investors: {sum(investor.money for investor in self.investors)/len(self.investors):.0f}€")
        log.info(f"Average number of investments: {sum(len(investor.investments) for investor in self.investors)/len(self.investors):.1f}")

        # log 5 best investors
        best = sorted(self.investors, key=lambda investor: investor.money, reverse=True)[:5]
        log.info(f"Best investors: {', '.join(str(investor) for investor in best)}")
        for investor in best:
            log.info(f"  {investor}")

        # log % of traders alive
        log.info(f"Traders alive: {len(self.traders)}/{len(self.traders + self.traders_graveyard)}")
        log.info(f"Average money of alive traders: {sum(trader.money for trader in self.traders)/len(self.traders):.0f}€")

        # log % of traders with a job
        employed = [trader for trader in self.traders if trader.ceo is not None]
        log.info(f"Traders employed: {len(employed)}/{len(self.traders)}")

        # log average salary
        log.info(f"Average salary: {sum(trader.salary for trader in employed)/len(employed):.0f}€")

        # log 5 best traders
        best = sorted(self.traders, key=lambda trader: trader.money, reverse=True)[:5]
        log.info(f"Best traders: {', '.join(str(trader) for trader in best)}")
        for trader in best:
            log.info(f"  {trader} works for {trader.ceo}")
            log.info(f"     and has {trader.projects_estimator}")


    def loop(self):
        self.hire_traders()

        self.estimate_projects()

        self.mature_projects()

        self.pay_salaries()

        self.end_turn()


                

if __name__ == "__main__":
    m = Market()
    m.add_projects(100)
    m.add_investors(50)
    m.add_traders(50)

    for i in range(1000):
        log.info(f"Turn: {i}")
        m.loop()
        if i % 5 == 0:
            m.log()
            m.add_projects(50)
            m.add_investors(10)
            m.add_traders(10)
