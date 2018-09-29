# -*- coding: utf-8 -*-
"""
Created on Thu Jul  5 18:12:31 2018

@author: Rignak
"""
import math
from . import Sprites

class Bullet():
    def __init__(self, ship, bulletSprite):
        self.damage = ship.damage

        angle = ship.sprite.angle/180*math.pi

        self.sprite = Sprites.Sprite(bulletSprite, ship.sprite.rect.center)
        self.sprite.speed = [ship.sprite.speed[0] + ship.bulletSpeed*math.cos(angle),
                             -(ship.sprite.speed[1] + ship.bulletSpeed*math.sin(angle)),
                             0]
        if self.sprite.speed[0]:
            self.sprite.angle = math.atan(-self.sprite.speed[1]/self.sprite.speed[0])/math.pi*180
        else:
            self.sprite.angle = [90, 270][self.sprite.speed[1]>0]
