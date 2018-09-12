# -*- coding: utf-8 -*-
"""
Created on Thu Jul  5 18:03:23 2018

@author: Rignak
"""

import pygame
from . import Ship
from os.path import join
import json
from pygame.sprite import spritecollide, collide_mask
import random
import math

class Screen():
    def __init__(self, size, background):
        self.font = pygame.font.SysFont("monospace", 15)
        self.size = size
        self.display = pygame.display.set_mode(self.size, pygame.RESIZABLE)
        self.ships = []
        self.background = background
        self.ui = {'score'}


        with open(join('res', 'json', 'ships.json')) as file:
            self.shipsBasis = json.loads(file.read())
        with open(join('res', 'json', 'battles.json')) as file:
            self.battlesBasis = json.loads(file.read())

    def Refresh(self):
        self.TrimSprites()
        self.display.blit(self.background, (0,0))

        if self.ships:
            score = self.ships[0].scorePlayer
        else:
            score = 0
        scoreText = self.font.render(str(score), 1, (255, 255, 255))
        self.display.blit(scoreText, (0,0))

        for ship in self.ships:
            if ship.killedInDuty:
                continue
            ship.sprite.Rotate(ship.sprite.angle)
            ship.lastFire += 1
            self.display.blit(ship.sprite.image, ship.sprite.rect)
            for bullet in ship.bullets:
                bullet.sprite.Rotate(bullet.sprite.angle)
                self.display.blit(bullet.sprite.image, bullet.sprite.rect)
        pygame.display.update()

    def InitiateBattle(self, battleType='baseBattle'):
        battle = self.battlesBasis[battleType]
        self.AddShips(battle['ships'])

    def AddShips(self, ships):
        for ship, data in ships.items():
            for team, coords in data.items():
                for x, y, angle in coords:
                    print(ship, x, y, angle, team)
                    self.ships.append(Ship.Ship(self.shipsBasis[ship], (x, y), int(team), angle))

        from . import Sprites
        self.ships[0].sprite = Sprites.Sprite('player.png', self.ships[0].sprite.rect.center)
        self.ships[0].sprite.speed = [0, 0, 0]
        self.ships[0].sprite.angle = 0
        return self.ships

    def MoveSprites(self):
        for ship in self.ships:
            if not ship.killedInDuty:
                ship.sprite.Move()
            for bullet in ship.bullets:
                bullet.sprite.Move()

    def GetBulletCollisions(self):
        collisions = []
        for i, ship1 in enumerate(self.ships):
            bullets = [bullet.sprite for bullet in ship1.bullets]
            for j, ship2 in enumerate(self.ships):
                if ship2.killedInDuty:
                    continue
                # For performance (and laziness) we suppose that:
                    # 1/ A ship cannot shot itself
                    # 2/ The delay is too high to have one ship shooted twice by one ship in one frame
                if ship2 == ship1:
                    continue
                collision =  spritecollide(ship2.sprite, bullets,
                                           False, collide_mask)
                if not collision:
                    continue
                for k, bullet in enumerate(ship1.bullets):
                    x, y = bullet.sprite.rect.center
                    if bullet.sprite == collision[0]:
                        ship1.bullets.pop(k)
                        collisions.append(((ship1, i), (ship2,j), (bullet,k)))
                        break
        return collisions

    def TrimSprites(self):
        i = 0
        while i < len(self.ships):
            j = 0
            ship = self.ships[i]
            while j < len(ship.bullets):
                x, y = ship.bullets[j].sprite.rect.center
                if x < 0 or x > self.size[0] or y < 0 or y > self.size[1]:
                    self.ships[i].bullets.pop(j)
                else:
                    j += 1
            x, y = ship.sprite.rect.center
            if x < 0 or x > self.size[0] or y < 0 or y > self.size[1]:
                self.ships.pop(i)
            else:
                i += 1

    def GetShipCollisions(self):
        collisions = []
        for i, ship1 in enumerate(self.ships):
            if ship1.killedInDuty:
                continue
            for j, ship2 in enumerate(self.ships):
                if ship2.killedInDuty:
                    continue
                if ship2 == ship1:
                    continue
                collision = spritecollide(ship2.sprite, [ship1.sprite],
                                           False, collide_mask)
                if collision:
                    collisions.append(((ship1, i), (ship2, j)))

        return collisions

    def Repop(self):
        p = random.random()
        if p < 0.015 and len(self.ships)<10:
            side = int(random.random()*4)
            if side == 0:
                x, y = 0, int(random.random()*self.size[1])
            elif side == 1:
                x, y = 1000, int(random.random()*self.size[1])
            elif side == 2:
                x, y = int(random.random()*self.size[0]), 0
            elif side == 3:
                x, y = int(random.random()*self.size[0]), 1000
            arad = math.atan((self.size[0]/2-x)/(self.size[1]/2-y))-math.pi/2*[-1,1][y < self.size[1]/2]
            arad += random.uniform(-math.pi/8, math.pi/8)
            a = arad*180/math.pi
            ship = Ship.Ship(self.shipsBasis['cruiser'], (x, y), 1, a)
            ship.Motor([1,0])
            self.ships.append(ship)
