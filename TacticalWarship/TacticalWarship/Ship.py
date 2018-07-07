# -*- coding: utf-8 -*-
"""
Created on Thu Jul  5 18:12:31 2018

@author: Rignak
"""
from os.path import join
from . import Bullet
import pygame
import math

class Ship():
    def __init__(self, ship, xy, team, angle):
        self.xy = xy
        self.angle = angle
        self.team = team
        self.score = 0
        
        self.hp = ship['hp']
        self.shield = ship['shield']
        
        self.acceleration = ship['acceleration']      
        self.speed = [0, 0, 0]
        self.inertia = ship['inertia']
        
        self.bullets = []
        self.lastFire = 0
        self.fireDelay = ship['fireDelay']
        self.damage = ship['damage']
        self.bulletSpeed = ship['bulletSpeed']
        
        self.sprite = None
        self.origSprite = pygame.image.load(join('res', 'img', ship['sprite']))
        self.image = self.origSprite
        self.rect = self.image.get_rect()
        self.rect.center = xy
        
    def Motor(self, command):
        factor = command[0]*self.inertia*self.acceleration[['rear', 'front'][command[0] > 0]]
        angle = self.angle/180*math.pi
        self.speed[0] += factor*math.cos(angle)
        self.speed[1] -= factor*math.sin(angle)
        self.speed[2] += command[1]*self.inertia*self.acceleration['side']
        
    def Fire(self):
        if self.lastFire > self.fireDelay:
            self.bullets.append(Bullet.Bullet(self))
            self.lastFire = 0
        
    def Move(self):
        if self.speed[0]:
            self.xy[0] += self.speed[0]
        if self.speed[1]:
            self.xy[1] += self.speed[1]
        if self.speed[2]:
            self.angle = (self.angle+self.speed[2])%360
        self.rect.center = self.xy
            
    def Rotate(self):
        self.image = pygame.transform.rotate(self.origSprite, self.angle)
        x, y = self.rect.center  # Save its current center.
        self.rect = self.image.get_rect()  # Replace old rect with new rect.
        self.rect.center = (x, y)  # Put the new rect's center at old center.
        