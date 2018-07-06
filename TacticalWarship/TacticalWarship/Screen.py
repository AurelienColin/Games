# -*- coding: utf-8 -*-
"""
Created on Thu Jul  5 18:03:23 2018

@author: Rignak
"""

import pygame
from . import Ship
from os.path import join
import json

class Screen():
    def __init__(self, size, background):
        self.size = size
        self.display = pygame.display.set_mode(self.size, pygame.RESIZABLE)
        
        self.ships = []
        self.bullets = []
        self.background = background
        self.ui = {'score'}
    
    def Refresh(self):        
        self.display.blit(self.background, (0,0))
        for ship in self.ships:
            ship.Rotate()
            self.display.blit(ship.image, ship.rect)
            for bullet in ship.bullets:
                self.display.blit(utils.RotateSprite(bullet), bullet.xy)
        pygame.display.update()
                
    def InitiateBattle(self):
        with open(join('res', 'json', 'battles.json')) as file:
            battles = json.loads(file.read())
        battle = battles['baseBattle']
        self.AddShips(battle['ships'])
        
    def AddShips(self, ships):
        with open(join('res', 'json', 'ships.json')) as file:
            shipsBasis = json.loads(file.read())
        
        for team in [0,1]:
            for ship, nb in ships.items():
                for j in range(nb):
                    xy = [self.size[1]*[0.1, 0.9][team], self.size[0]//(nb+1)*(j+1)]
                    self.ships.append(Ship.Ship(shipsBasis[ship], xy,
                                                team, [0, 180][team]))
        return self.ships
        
    def MoveShips(self):
        for ship in self.ships:
            ship.Move()