import pygame
import os
from PIL import Image
from random import randint, random

pygame.init()

WIN_WIDTH = 800
WIN_HEIGHT = 800
WIN_DIMS = (WIN_WIDTH, WIN_HEIGHT)

WHITE = (255, 255, 255)

DISP = pygame.display.set_mode(WIN_DIMS)
pygame.display.set_caption('Kill The Cars')

p_car_img = Image.open(os.path.join('car.png'))
p_car_img.thumbnail((80, 80), Image.ANTIALIAS)
p_car_img = p_car_img.rotate(90, expand=True)

e_car_img = Image.open(os.path.join('car2.png'))
e_car_img.thumbnail((80, 80), Image.ANTIALIAS)
e_car_img = e_car_img.rotate(180, expand=True)

fruit_img = Image.open(os.path.join('apple.png'))
fruit_img.thumbnail((80, 80), Image.ANTIALIAS)

P_CAR = pygame.image.fromstring(
    p_car_img.tobytes(),
    p_car_img.size,
    p_car_img.mode
)

E_CAR = pygame.image.fromstring(
    e_car_img.tobytes(),
    e_car_img.size,
    e_car_img.mode
)

FRUIT = pygame.image.fromstring(
    fruit_img.tobytes(),
    fruit_img.size,
    fruit_img.mode
)

class Player:
    def __init__(self, img, x, y):
        self.img = img
        self.img_dims = img.get_size()
        self.rect = self.img.get_rect()
        self.rect.topleft = (self.x, self.y) = (x, y)

    def move(self, dx):
        self.x += dx
        self.rect.x += dx

    def render(self, win):
        win.blit(self.img, (self.x, self.y))

class Projectile:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.rect = pygame.Rect(x, y, 5, 20)

    def move(self, dy):
        self.y += dy
        self.rect.y += dy

    def render(self, win):
        pygame.draw.rect(win, WHITE, self.rect)

class Fruit:
    def __init__(self, img, x, y):
        self.img = img
        self.img_dims = img.get_size()
        self.rect = img.get_rect()
        self.rect.topleft = (self.x, self.y) = (x, y)

    def move(self, dy):
        self.y += dy
        self.rect.y += dy

    def render(self, win):
        win.blit(self.img, (self.x, self.y))

class FruitArray:
    def __init__(self, density, y, lane_xs):
        self.density = density
        self.start = y
        self.fruits = []
        self.lane_xs = lane_xs

    def create_fruit(self):
        new_fruit = Fruit(FRUIT, randint(self.lane_xs[0], self.lane_xs[1]), self.start)

        for fruit in self.fruits:
            if fruit.rect.colliderect(new_fruit.rect):
                return

        self.fruits.append(new_fruit)

    def reset(self):
        self.fruits = []

    def move_fruits(self):
        if random() <= self.density:
            self.create_fruit()

        for fruit in self.fruits:
            fruit.move(7)

            if fruit.y >= WIN_HEIGHT:
                self.fruits.remove(fruit)

    def render(self, win):
        for fruit in self.fruits:
            fruit.render(win)

class TrafficCar:
    def __init__(self, img, x, y):
        self.img = img
        self.img_dims = img.get_size()
        self.rect = img.get_rect()
        self.rect.topleft = (self.x, self.y) = (x, y)

    def move(self, dy):
        self.y += dy
        self.rect.y += dy

    def render(self, win):
        win.blit(self.img, (self.x, self.y))

class Traffic:
    def __init__(self, density, y, lane_xs):
        self.density = density
        self.cars = []
        self.lane_xs = lane_xs
        self.start = y

    def create_car(self):
        new_car = TrafficCar(E_CAR, randint(self.lane_xs[0], self.lane_xs[1]), self.start)

        for car in self.cars:
            if car.rect.colliderect(new_car.rect):
                return

        self.cars.append(new_car)

    def reset(self):
        self.cars = []

    def move_cars(self):
        if random() <= self.density:
            self.create_car()

        for car in self.cars:
            car.move(10)

            if car.y >= WIN_HEIGHT:
                self.cars.remove(car)

    def render(self, win):
        for car in self.cars:
            car.render(win)

class GUI:
    def __init__(self):
        self.player = Player(P_CAR, 200, 680)
        self.traffic = Traffic(0.03, -80, (21, 339))
        self.fruits = FruitArray(0.02, -80, (21, 339))
        self.play_area_x_bounds = (20, 420)
        self.projectiles = []
        self.score_font = pygame.font.SysFont('Arial', 30)
        self.instruction_font = pygame.font.SysFont('Arial', 15)
        self.score = 0
        self.score_coords = (440, 20)
        self.instructions = [
            ["Press the Left and Right arrow keys to move your car.", (440, 200)],
            ["Avoid/Kill Red cars while collecting fruits.", (440, 230)],
            ["Shoot projectiles by pressing A.", (440, 260)]
        ]

    def move_player(self, move_dir):
        if move_dir == 'R' and self.player.rect.x + 5 < 420 - self.player.img_dims[0]:
            self.player.move(5)
        elif move_dir == 'L' and self.player.rect.x - 5 > 20:
            self.player.move(-5)

    def move_traffic(self):
        self.traffic.move_cars()

    def move_projectiles(self):
        for proj in self.projectiles:
            proj.move(-20)

    def move_fruits(self):
        self.fruits.move_fruits()

    def move_entities(self):
        self.move_traffic()
        self.move_projectiles()
        self.move_fruits()

    def fire_projectile(self):
        x = self.player.rect.x + 17.5
        y = self.player.rect.y - 10

        self.projectiles.append(Projectile(x, y))

    def check_projectile_hits(self):
        for car in self.traffic.cars:
            for proj in self.projectiles:
                if car.rect.colliderect(proj.rect) or car.rect.contains(proj.rect):
                    self.traffic.cars.remove(car)
                    self.projectiles.remove(proj)
                    self.score += 100

                if proj.y <= 0:
                    self.projectiles.remove(proj)

    def check_car_collision(self):
        for car in self.traffic.cars:
            if self.player.rect.colliderect(car.rect):
                return True

        self.score += 1
        return False

    def check_fruit_collision(self):
        for fruit in self.fruits.fruits:
            if self.player.rect.colliderect(fruit.rect):
                self.score += 100
                self.fruits.fruits.remove(fruit)

    def render_score(self, win):
        win.blit(self.score_font.render(f"Score: {self.score}", True, WHITE), self.score_coords)

    def render_instructions(self, win):
        for ins in self.instructions:
            win.blit(self.instruction_font.render(ins[0], True, WHITE), ins[1])

    def render_play_area(self, win):

        for coord in self.play_area_x_bounds:
            pygame.draw.line(
                win,
                WHITE,
                (coord, 0),
                (coord, WIN_HEIGHT)
            )

    def render_entities(self, win):
        self.player.render(win)
        self.traffic.render(win)
        self.fruits.render(win)
        for proj in self.projectiles:
            proj.render(win)

    def render(self, win):
        DISP.fill((25, 25, 25))

        self.render_play_area(win)
        self.render_entities(win)
        self.render_score(win)
        self.render_instructions(win)

        pygame.display.update()

def quit_game():
    pygame.quit()
    quit()


def main_loop():

    clock = pygame.time.Clock()
    gui = GUI()

    pressing_r = False
    pressing_l = False
    fired = False
    projectile_cooldown = 0

    while True:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    pressing_r = True
                elif event.key == pygame.K_LEFT:
                    pressing_l = True
                elif event.key == pygame.K_a and projectile_cooldown == 0:
                    gui.fire_projectile()
                    fired = True
            
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_RIGHT:
                    pressing_r = False
                elif event.key == pygame.K_LEFT:
                    pressing_l = False

        if fired:
            projectile_cooldown = (projectile_cooldown + 1) % 20
            if projectile_cooldown == 0:
                fired = False

        if pressing_l:
            gui.move_player('L')
        elif pressing_r:
            gui.move_player('R')

        if gui.check_car_collision():
            quit_game()

        gui.check_projectile_hits()
        gui.check_fruit_collision()
        gui.move_entities()
        gui.render(DISP)

main_loop()