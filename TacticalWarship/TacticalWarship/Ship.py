# -*- coding: utf-8 -*-
"""
Created on Thu Jul  5 18:12:31 2018

@author: Rignak
"""
from os.path import join
from pygame.image import load
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
        self.speed = [0, 0]
        self.inertia = ship['inertia']
        
        self.bullets = []
        self.fireDelay = ship['fireDelay']
        self.damage = ship['damage']
        self.bulletSpeed = ship['bulletSpeed']
        
        self.sprite = None
        self.origSprite = load(join('res', 'img', ship['sprite']))
        self.image = self.origSprite
        self.rect = self.image.get_rect()
        self.rect.center = xy
        
    def Motor(self, command):
        self.speed[0] += command[0]*self.inertia*self.acceleration[['rear', 'front'][command[0] > 0]]
        self.speed[1] += command[1]*self.inertia*self.acceleration['side']
        
    def Move(self):
        self.angle += self.speed[1]%360
        if self.speed[0]:
            print(self.speed, self.angle)
            self.xy[0] += self.speed[0]*math.cos(self.angle/180*math.pi)
            self.xy[1] += self.speed[0]*math.sin(self.angle/180*math.pi)
            
    def Rotate(self):
        self.image = pygame.transform.rotate(self.origSprite, self.angle)
        x, y = self.rect.center  # Save its current center.
        self.rect = self.image.get_rect()  # Replace old rect with new rect.
        self.rect.center = (x, y)  # Put the new rect's center at old center.
        
    def Fire(self):
        self.bullets.append(Bullet.Bullet(self))
        