import random
import pygame

from pygame import Vector2

# agent class with position
class Agent:
    def __init__(self, x, y):
        self.position = Vector2(x, y)
        self.velocity = Vector2(random.randint(-1, 1), random.randint(-1, 1))
        self.acc = Vector2(0, 0)
        self.size = random.randint(1, 5)
        self.force = Vector2(0, 0)

        self.color = random.randint(5, 255), random.randint(5, 255), random.randint(5, 255)

        self.current_objective = 0
        self.introversion = (6 - self.size) * 3

    def populate_objectives(self, l):
        self.current_objective = random.randint(0, l-1)

    def apply_force(self, force):
        self.force += force

    def update(self, target):
        self.apply_force((target - self.position).normalize() * 0.5)

        self.acc = -self.velocity * self.velocity.length() * 0.2
        self.velocity += self.acc + self.force
        self.force = Vector2(0, 0)
        self.position += self.velocity

    def constrain(self, width, height):
        self.position.x = max(0, min(self.position.x, width))
        self.position.y = max(0, min(self.position.y, height))
        self.velocity.x = max(-10, min(self.velocity.x, 10))
        self.velocity.y = max(-10, min(self.velocity.y, 10))
        self.acc.x = max(-10, min(self.acc.x, 10))
        self.acc.y = max(-10, min(self.acc.y, 10))

# game class with screen and agent
class Game:
    def __init__(self):
        self.width = 800
        self.height = 600
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.clock = pygame.time.Clock()
        self.running = True
        
        self.cities = [[Vector2(self.width * random.random(), self.height * random.random()), 0] for _ in range(50)]

        self.agents = []
        self.populate_agents()
        for agent in self.agents:
            agent.populate_objectives(len(self.cities))

    def run(self):
        i = 0
        while self.running:
            self.events()
            self.update()
            
            if(i > 1000):
                self.clock.tick(60)
                self.draw()

            i += 1

    def populate_agents(self):
        for _ in range(200):
            self.agents.append(Agent(self.width * random.random(), self.height * random.random()))

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def update(self):
        for agent in self.agents:
            if agent.position.x > self.width or agent.position.x < 0:
                agent.velocity.x *= -1
            if agent.position.y > self.height or agent.position.y < 0:
                agent.velocity.y *= -1

            target = self.cities[agent.current_objective][0]
            if (target - agent.position).length() < agent.size + 15:
                self.cities[agent.current_objective][1] += 1

                p = list(range(len(self.cities)))
                p.remove(agent.current_objective)
                w = [k[1] for i, k in enumerate(self.cities) if i != agent.current_objective]
                if sum(w) == 0:
                    w = None
                agent.current_objective = random.choices(p, w)[0]

            for other in self.agents:
                if agent is other:
                    continue
                distance = agent.position.distance_to(other.position)
                if distance < 20:
                    vec = agent.position - other.position
                    factor = 1 / (vec.length())
                    agent.apply_force(vec.normalize() * factor * agent.introversion)

            agent.apply_force(Vector2(0, 0))

        for agent in self.agents:
            target = self.cities[agent.current_objective][0]
            agent.update(target)

        for agent in self.agents:
            agent.constrain(self.width, self.height)


    def draw(self):
        self.screen.fill((0, 0, 0))

        for agent in self.agents:
            pygame.draw.line(self.screen, (255, 0, 0), (int(agent.position.x), int(agent.position.y)), (int(self.cities[agent.current_objective][0].x), int(self.cities[agent.current_objective][0].y)), 1)
            pygame.draw.circle(self.screen, agent.color, (int(agent.position.x), int(agent.position.y)), agent.size)

        for city in self.cities:
            #pygame.draw.circle(self.screen, (255, 255, 255), (int(city[0].x), int(city[0].y)), 3)
            font = pygame.font.SysFont('Arial', 12)
            text = font.render(str(city[1]), True, (255, 255, 255))
            self.screen.blit(text, (int(city[0].x) - text.get_width() // 2, int(city[0].y) - text.get_height() // 2))

        pygame.display.flip()


if __name__ == '__main__':
    pygame.init()
    game = Game()
    game.run()
    pygame.quit()
    quit()