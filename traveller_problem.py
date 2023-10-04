from dis import show_code
import pygame as pg
import random
import tqdm

class Map:
    def __init__(self, length):
        self.size = 500, 500
        self.screen = pg.display.set_mode(self.size)
        self.clock = pg.time.Clock()
        self.running = True
        self.font = pg.font.SysFont('Arial', 20)
        self.text = self.font.render('Hello', True, (255, 255, 255))
        self.cities = [pg.Vector2(random.randint(0, 500), random.randint(0, 500)) for _ in range(length)]
        self.compute_origin_destination()

    def compute_origin_destination(self):
        self.origin_destination = []
        for i in range(len(self.cities)):
            self.origin_destination.append([])
            for city in self.cities:
                self.origin_destination[i].append(self.cities[i].distance_to(city))

    def fitness(self, path):
        return sum(self.origin_destination[path[i]][path[i + 1]] for i in range(len(path) - 1))

    def show_path(self, path):
        self.screen.fill((0, 0, 0))
        for city in self.cities:
            # square
            pg.draw.rect(self.screen, (255, 255, 255), (int(city.x) - 5, int(city.y) - 5, 10, 10))

        for i in range(len(path) - 1):
            pg.draw.line(self.screen, (255, 255, 255), self.cities[path[i]], self.cities[path[i + 1]], 1)
        pg.display.flip()

    def handle_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.running = False
            # if mouse pressed
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                # remove closest city
                closest = self.cities[0]
                for city in self.cities:
                    if closest != city and city.distance_to(pg.mouse.get_pos()) < closest.distance_to(pg.mouse.get_pos()):
                        closest = city
                print(f"removing {closest}")
                self.cities.remove(closest)
                self.compute_origin_destination()
            
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 3:
                # add city
                self.cities.append(pg.Vector2(pg.mouse.get_pos()))
                self.compute_origin_destination()


def main():
    n = 150

    map = Map(n)
    
    best_path = [0, 1]

    for i in tqdm.tqdm(range(n)):
        if i in best_path:
            continue

        min_ = 1e9
        for j in range(len(best_path) - 1):
            path = best_path[:]
            path.insert(j + 1, i)
            fitness = map.fitness(path)
            if fitness < min_:
                min_ = fitness
                index = j + 1

        best_path.insert(index, i)

    best_fitness = map.fitness(best_path)
    map.show_path(best_path)

    while map.running:
        map.handle_events()
        if len(best_path) > len(map.cities):
            best_path.remove(len(map.cities))
            map.show_path(best_path)
        if len(best_path) < len(map.cities):
            min_ = 1e9
            for j in range(len(best_path) - 1):
                path = best_path[:]
                path.insert(j + 1, len(map.cities)-1)
                fitness = map.fitness(path)
                if fitness < min_:
                    min_ = fitness
                    index = j + 1
            best_path.insert(index, len(map.cities)-1)
            map.show_path(best_path)
        n = len(best_path)

        for _ in range(4):
            path = list(best_path)
            i = random.randint(0, n - 1)
            j = random.randint(0, n - 1)
            path[i], path[j] = path[j], path[i]
            fitness = map.fitness(path)
            if fitness < best_fitness:
                best_fitness = fitness
                best_path = path
                print(best_fitness)
                map.show_path(best_path)
                map.clock.tick(60)

if __name__ == '__main__':
    pg.init()
    main()