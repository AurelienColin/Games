import json
import os
import random
import math

import pygame

from Rignak_Games.Asteroid.Ships import Ship
from Rignak_Games.Sprites import SCALING_FACTOR

FONT = 'monospace'
FONT_SIZE = 15
MARGIN = 0.1

REPOPING_SHIP_TEAM = 1
REPOPING_SHIP_NAME = 'cruiser'
REPOPING_PROBABILITY = 0.01
MAX_SHIPS = 10


class Screen:
    def __init__(self, size, background, font=FONT, font_size=FONT_SIZE, scaling_factor=SCALING_FACTOR):
        self.size = int(size[0]*scaling_factor), int(size[1]*scaling_factor)
        self.background = background
        self.display = pygame.display.set_mode(self.size, pygame.RESIZABLE)
        self.fps_clock = pygame.time.Clock()
        self.ships = []
        self.font = pygame.font.SysFont(font, font_size)

    def refresh(self, fps):
        self.display.blit(self.background, (0, 0))

        for ship in self.ships:
            for bullet in ship.bullets:
                x, y = bullet.sprite.rect.center
                x -= bullet.sprite.current_size[0] // 2
                y -= bullet.sprite.current_size[1] // 2
                self.display.blit(bullet.sprite.current_sprite, (x, y))
            if not ship.dead:
                x, y = ship.sprite.rect.center
                x -= ship.sprite.current_size[0] // 2
                y -= ship.sprite.current_size[1] // 2
                self.display.blit(ship.sprite.current_sprite, (x, y))

        if self.ships:
            score = self.ships[0].score
        else:
            score = 0
        score_text = self.font.render(str(int(score)), 1, (255, 255, 255))
        fps_text = self.font.render(str(int(self.fps_clock.get_fps())), True, pygame.Color('white'))
        self.display.blit(score_text, (0.05*self.size[0], 0.05*self.size[1]))
        self.display.blit(fps_text, (0.05*self.size[0], 0.10*self.size[1]))
        if not fps:
            self.fps_clock.tick(9999)
        else:
            self.fps_clock.tick(fps)
        pygame.display.update()

    def initiate_battle(self, battle_name, battle_filename):
        with open(battle_filename, 'r') as battle_file:
            battles = json.load(battle_file)
        for ship_name, position in battles[battle_name]['ships']:
            self.add_ship(ship_name, position['team'], position['x'], position['y'], position['angle'])

    def add_ship(self, ship_name, team, x, y, angle):
        self.ships.append(Ship(ship_name, team,
                               x=x * self.size[0],
                               y=y * self.size[1],
                               angle=angle))

    def pass_turn(self):
        for ship in self.ships:
            ship.pass_turn()
        self.repop()

    def repop(self, repoping_probability=REPOPING_PROBABILITY, margin=MARGIN, max_ships=MAX_SHIPS,
              ship_name=REPOPING_SHIP_NAME, team=REPOPING_SHIP_TEAM):
        margin_a, margin_b = margin, 1 - margin
        height, width = self.size

        p = random.random()
        if p > repoping_probability or len(self.ships) > max_ships:
            return
        x = int((random.random() * 0.9 + 0.05) * height)
        y = int((random.random() * 0.9 + 0.05) * width)
        side = int(random.random() * 4)
        if side == 0:
            x = margin_a * height
        elif side == 1:
            x = margin_b * height
        elif side == 2:
            y = margin_a * width
        elif side == 3:
            y = margin_b * width

        angle_radian = math.atan((height / 2 - x) / (width / 2 - y+0.1)) - math.pi / 2 * [-1, 1][y < width / 2]
        angle = angle_radian * 180 / math.pi

        ship = Ship(ship_name, team, x=x, y=y, angle=angle)
        ship.use_motor([0, 1, 0, 0, 0])
        ship.use_motor([0, 1, 0, 0, 0])

        self.ships.append(ship)

    def trim(self):
        height, width = self.size
        i = 0
        while i < len(self.ships):
            ship = self.ships[i]
            j = 0
            while j < len(ship.bullets):
                x, y = ship.bullets[j].sprite.rect.center
                x += ship.bullets[j].sprite.original_size[0]
                y += ship.bullets[j].sprite.original_size[1]
                if x < 0 or x > height or y < 0 or y > width:
                    self.ships[i].bullets.pop(j)
                else:
                    j += 1
            x, y = ship.sprite.rect.center
            x += ship.sprite.original_size[0]
            y += ship.sprite.original_size[1]
            if x < 0 or x > height or y < 0 or y > width:
                self.ships[i].kill()
                if i != 0 and not ship.bullets:
                    self.ships.pop(i)
                else:
                    i += 1
            else:
                i += 1
