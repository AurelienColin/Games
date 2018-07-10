# -*- coding: utf-8 -*-
"""
Created on Thu Jul  5 18:00:07 2018

@author: Rignak
"""
from TacticalWarship import Screen
import sys
import pygame
from pygame.locals import KEYDOWN, K_RETURN, QUIT, K_UP, K_DOWN, K_LEFT, K_RIGHT

from os.path import join

def Launcher():
    pygame.init()
    global screenDim
    screenDim = (1000,1000)
    background = pygame.image.load(join('res', 'img', 'bg_main.png'))
    screen = Screen.Screen(screenDim, background)
    
    return screen


def Loop(screen):
    mainClock = pygame.time.Clock()
    while True:
        mainClock.tick(10)
        for event in pygame.event.get():
            if event.type == QUIT:  # The game is closed
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                keys = pygame.key.get_pressed()
                if keys[K_UP]:
                    screen.ships[0].Motor([1,0])
                if keys[K_DOWN]:
                    screen.ships[0].Motor([-1,0])
                if keys[K_RIGHT]:
                    screen.ships[0].Motor([0,-1])
                if keys[K_LEFT]:
                    screen.ships[0].Motor([0,1])
                if keys[K_RETURN]:
                    screen.ships[0].Fire()
        
        screen.MoveSprites()
        collisions = screen.GetBulletCollisions()
        for ship1, ship2, bullet in collisions:
            dmg = GetDamage(ship1, ship2, bullet)
            score = screen.ships[ship2[1]].ApplyDamage(dmg)
            screen.ships[ship1[1]].scorePlayer += score
        screen.Refresh()
    pass

def GetDamage(ship1, ship2, bullet):
    angle = (bullet[0].sprite.angle-ship2[0].sprite.angle)%360
    if angle > 120 and angle < 240:
        part = "front"
    elif angle <60 or angle > 300:
        part = "rear"
    else:
        part = "side"
    dmg = ship1[0].damage*ship2[0].shield[part]
    return dmg
    
if __name__ == '__main__':
    screen = Launcher()
    screen.Refresh()
    screen.InitiateBattle()
    Loop(screen)