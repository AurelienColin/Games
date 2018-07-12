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
        mainClock.tick(30)
        for event in pygame.event.get():
            if event.type == QUIT:  # The game is closed
                pygame.quit()
                sys.exit()
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
            dmg = GetBulletDamage(ship1[0], ship2[0], bullet[0])
            score = screen.ships[ship2[1]].ApplyDamage(dmg)
            screen.ships[ship1[1]].scorePlayer += score
            screen.ships[ship2[1]].scorePlayer -= score
            
        collisions = screen.GetShipCollisions()
        
        dmgs = []
        for ship1, ship2 in collisions:
            dmg = GetShipDamage(ship1[0], ship2[0])
            dmgs.append((ship1, ship2, dmg))
            
        for ship1, ship2, dmg in dmgs:
            score = screen.ships[ship2[1]].ApplyDamage(dmg)
            screen.ships[ship1[1]].scorePlayer += score
            screen.ships[ship2[1]].scorePlayer -= score
            
            # We also stop the ships (not calculating rebounce)
            screen.ships[ship1[1]].sprite.speed = [0, 0, 0]
            screen.ships[ship2[1]].sprite.speed = [0, 0, 0]
                        
            
        screen.Refresh()
    pass

def GetShipDamage(ship1, ship2):
    # This one is false since the ship not always move forward
    diffSpeedSquared = (ship1.sprite.speed[0]-ship2.sprite.speed[0])**2 + \
                       (ship1.sprite.speed[1]-ship2.sprite.speed[1])**2 
                       
    dmg = (10*ship2.shield['front']*diffSpeedSquared)
    return dmg

def GetBulletDamage(ship1, ship2, bullet):
    part = GetPart(bullet.sprite.angle, ship2.sprite.angle)
    dmg = ship1.damage*ship2.shield[part]
    return dmg
    
def GetPart(angle1, angle2):
    angle = (angle1-angle2)%360
    if angle > 120 and angle < 240:
        part = "front"
    elif angle <60 or angle > 300:
        part = "rear"
    else:
        part = "side"
    return part
    
    
if __name__ == '__main__':
    screen = Launcher()
    screen.Refresh()
    screen.InitiateBattle()
    Loop(screen)