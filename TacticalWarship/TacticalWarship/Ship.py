# -*- coding: utf-8 -*-
"""
Created on Thu Jul  5 18:12:31 2018

@author: Rignak
"""

from . import Bullet, Sprites
import math

class Ship():
    def __init__(self, ship, xy, team, angle, sprite, bulletSprite):
        self.team = team
        self.scorePlayer = 0
        self.killedInDuty = False
        self.score = ship['score']

        self.hp = ship['hp']
        self.shield = ship['shield']

        self.acceleration = ship['acceleration']

        self.bullets = []
        self.lastFire = 0
        self.fireDelay = ship['fireDelay']
        self.damage = ship['damage']
        self.bulletSpeed = ship['bulletSpeed']
        self.bulletSprite = bulletSprite

        self.sprite = Sprites.Sprite(sprite, xy)
        self.sprite.speed = [0, 0, 0]
        self.sprite.angle = angle

        self.killedInDuty = False

    def Motor(self, command):
        self.sprite.speed[0] *= 0.7
        self.sprite.speed[1] *= 0.7
        if command[0] == 1:
            factor = self.acceleration['front']
        elif command[1] == 1:
            factor = -self.acceleration['rear']
        else:
            factor = 0
        if command[3] == 1:
            self.sprite.angle += 45
#            self.sprite.speed[2] += self.acceleration['side']
        elif command[4] == 1:
            self.sprite.angle -= 45
#            self.sprite.speed[2] -= self.acceleration['side']
        self.sprite.angle = self.sprite.angle%360

        angle = self.sprite.angle/180*math.pi

        self.sprite.speed[0] += factor*math.cos(angle)
        self.sprite.speed[1] -= factor*math.sin(angle)


        if  self.sprite.speed[0] > 20:
            self.sprite.speed[0] = 20
        elif self.sprite.speed[0]< -20:
            self.sprite.speed[0] = -20
        if  self.sprite.speed[1] > 20:
            self.sprite.speed[1] = 20
        elif self.sprite.speed[1]< -20:
            self.sprite.speed[1] = -20
        if  self.sprite.speed[2] > 20:
            self.sprite.speed[2] = 20
        elif self.sprite.speed[2]< -20:
            self.sprite.speed[2] = -20

    def Fire(self):
        reward = 0
        if self.lastFire > self.fireDelay:
            reward = -1
            self.bullets.append(Bullet.Bullet(self, self.bulletSprite))
            self.lastFire = 0
        return reward

    def ApplyDamage(self, dmg):
        score = min(self.hp, dmg)*self.score['onDamage']
        self.hp -= dmg
        if self.hp <= 0:
            self.Kill()
            score += self.score['onKill']
        return score

    def Kill(self):
        # Should not remove entirely because bullet are still pending
        self.killedInDuty = True