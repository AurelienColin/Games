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
    def __init__(self, size, background, FACTOR = 1):
        with open(join('res', 'json', 'ships.json')) as file:
            self.shipsBasis = json.loads(file.read())
        with open(join('res', 'json', 'battles.json')) as file:
            self.battlesBasis = json.loads(file.read())
            self.sprites = {'player': pygame.image.load(join('res', 'img', 'player.png')),
                            'cruiser': pygame.image.load(join('res', 'img', 'cruiser.png')),
                            'bullet': pygame.image.load(join('res', 'img', 'bullet.png'))}
            for key in self.sprites:
                rect = self.sprites[key].get_rect()
                self.sprites[key] = pygame.transform.scale(self.sprites[key],
                                                           (int(FACTOR*rect.width), int(FACTOR*rect.height)))

        self.font = pygame.font.SysFont("monospace", 15)
        self.size = size
        self.display = pygame.display.set_mode(self.size, pygame.RESIZABLE)
        self.background =  background
        self.FPSCLOCK = pygame.time.Clock()
        self.margin = 0.03
        self.ships = []
        self.p = 1


    def Refresh(self, FPS):
        self.TrimSprites()
        self.display.blit(self.background, (0,0))


        for ship in self.ships:
            if ship.killedInDuty:
                continue
            ship.sprite.Rotate(ship.sprite.angle)
            ship.lastFire += 1
            self.display.blit(ship.sprite.image, ship.sprite.rect)
            for bullet in ship.bullets:
                bullet.sprite.Rotate(bullet.sprite.angle)
                self.display.blit(bullet.sprite.image, bullet.sprite.rect)

#        if self.ships:
#            score = self.ships[0].scorePlayer
#        else:
#            score = 0
#        scoreText = self.font.render(str(round(score, 1)), 1, (255, 255, 255))
#        self.display.blit(scoreText, (0,0))
#        fps = self.font.render(str(int(self.FPSCLOCK.get_fps())), True, pygame.Color('white'))
#        self.display.blit(fps, (0, 0))
        pygame.display.update()
        if FPS:
            self.FPSCLOCK.tick(FPS)
        else:
            self.FPSCLOCK.tick(9999)

    def InitiateBattle(self, battleType='baseBattle'):
        battle = self.battlesBasis[battleType]
        self.AddShips(battle['ships'])

    def AddShips(self, ships):
        for ship, data in ships.items():
            for team, coords in data.items():
                for x, y, angle in coords:
                    x*= self.size[0]
                    y*= self.size[1]
                    self.ships.append(Ship.Ship(self.shipsBasis[ship], (x, y),
                                                int(team), angle,
                                                self.sprites['cruiser'],
                                                self.sprites['bullet']))

        from . import Sprites
        self.ships[0].sprite = Sprites.Sprite(self.sprites['player'], self.ships[0].sprite.rect.center)
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
        f1, f2 = 1-self.margin, self.margin
        i = 0
        h,w = self.size
        while i < len(self.ships):
            j = 0
            ship = self.ships[i]
            while j < len(ship.bullets):
                x, y = ship.bullets[j].sprite.rect.center
                if x < 0 or x > h or y < 0 or y > w:
                    self.ships[i].bullets.pop(j)
                else:
                    j += 1
            x, y = ship.sprite.rect.center
            cond1 = (x < f2*h or x > f1*h or y < f2*w or y > f1*w)
            if (cond1 and i == 0) or (x<0 or x>h or y<0 or y>w):
                self.ships[i].killedInDuty = True
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
        f1, f2 = 1-self.margin, self.margin
        h, w = self.size
        p = random.random()
        if p < self.p:
            if self.p == 1:
                self.p = 0.015
            side = int(random.random()*4)
            if side == 0:
                x, y = f2*h, int(random.random()*w*0.9)
            elif side == 1:
                x, y = f1*h, int(random.random()*w*0.9)
            elif side == 2:
                x, y = int(random.random()*h*0.9), f2*w
            elif side == 3:
                x, y = int(random.random()*h*0.9), f1*w
            if w == 2*y:
                y = w/2+1
            arad = math.atan((h/2-x)/(w/2-y))-math.pi/2*[-1,1][y < w/2]
            arad += random.uniform(-math.pi/12, math.pi/12)
            a = arad*180/math.pi
            ship = Ship.Ship(self.shipsBasis['cruiser'], (x, y), 1, a,
                             self.sprites['cruiser'],
                             self.sprites['bullet'])
            ship.Motor([1, 0, 0, 0, 0, 1, 0, 1])
            ship.Motor([1, 0, 0, 0, 0, 1, 0, 1])
            self.ships.append(ship)
