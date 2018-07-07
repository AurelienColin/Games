# -*- coding: utf-8 -*-
"""
Created on Thu Jul  5 18:12:31 2018

@author: Rignak
"""
import math
from os.path import join
import pygame

class Bullet():
    def __init__(self, ship):
        self.xy = [ship.xy[0], ship.xy[1]]
        self.angle = ship.angle
        
        self.sprite = None
        self.origSprite = pygame.image.load(join('res', 'img', 'bullet.png'))
        self.image = self.origSprite
        self.rect = self.image.get_rect()
        self.rect.center = self.xy
        
        self.damage = ship.damage
        
        angle = self.angle/180*math.pi
        self.speed = [ship.speed[0] + ship.bulletSpeed*math.cos(angle),
                      - (ship.speed[1] + ship.bulletSpeed*math.sin(angle)),
                      0]
        
    def Move(self):
        if self.speed[0]:
            self.xy[0] += self.speed[0]
        if self.speed[1]:
            self.xy[1] += self.speed[1]
        self.rect.center = self.xy
        
    def Rotate(self):
        self.image = pygame.transform.rotate(self.origSprite, self.angle)
        x, y = self.rect.center  # Save its current center.
        self.rect = self.image.get_rect()  # Replace old rect with new rect.
        self.rect.center = (x, y)  # Put the new rect's center at old center.