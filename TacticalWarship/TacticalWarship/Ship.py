# -*- coding: utf-8 -*-
"""
Created on Thu Jul  5 18:12:31 2018

@author: Rignak
"""

from . import Bullet, Sprites
import math

class Ship():
    def __init__(self, ship, xy, team, angle):
        self.team = team
        self.scorePlayer = 0
        self.score = ship['score']
        
        self.hp = ship['hp']
        self.shield = ship['shield']
        
        self.acceleration = ship['acceleration']   
        self.inertia = ship['inertia']
        
        self.bullets = []
        self.lastFire = 0
        self.fireDelay = ship['fireDelay']
        self.damage = ship['damage']
        self.bulletSpeed = ship['bulletSpeed']   
        
        self.sprite = Sprites.Sprite(ship['sprite'], xy)
        self.sprite.speed = [0, 0, 0]
        self.sprite.angle = angle
        
    def Motor(self, command):
        factor = command[0]*self.inertia*self.acceleration[['rear', 'front'][command[0] > 0]]
        angle = self.sprite.angle/180*math.pi
        self.sprite.speed[0] += factor*math.cos(angle)
        self.sprite.speed[1] -= factor*math.sin(angle)
        self.sprite.speed[2] += command[1]*self.inertia*self.acceleration['side']
        
    def Fire(self):
        if self.lastFire > self.fireDelay:
            self.bullets.append(Bullet.Bullet(self))
            self.lastFire = 0
        
    def ApplyDamage(self, dmg):
        score = min(self.hp, dmg)*self.score['onDamage']
        self.hp -= dmg
        if self.hp <= 0:
            self.Kill()
            score += self.score['onKill']
        return score
        
    def Kill(self):
        # Should not remove entirely because bullet are still pending
        self.sprite = False