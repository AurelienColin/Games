# -*- coding: utf-8 -*-
"""
Created on Thu Jul  5 18:12:31 2018

@author: Rignak
"""
import math
from os.path import join
from pygame.image import load

class Bullet():
    def __init__(self, ship):
        self.speed = [ship.speed[0]+ship.bulletSpeed, ship.speed[1]]
        self.xy = ship.xy
        
        self.sprite = load(join('res', 'img', 'bullet.png'))
        
    def Move(self):
        self.xy[0] += self.speed[0]*math.cos(self.speed[1])
        self.xy[1] += self.speed[0]*math.sin(self.speed[1])