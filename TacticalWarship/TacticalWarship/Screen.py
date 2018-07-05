# -*- coding: utf-8 -*-
"""
Created on Thu Jul  5 18:03:23 2018

@author: Rignak
"""

import pygame

class Screen():
    def __init__(self, size, background):
        self.size = size
        self.display = pygame.display.set_mode(self.size, pygame.RESIZABLE)
        
        self.ships = {}
        self.bullets = []
        self.background = background
        self.ui = {'score'}
    
    def Refresh(self):        
        self.display.blit(self.background, (0,0))
        [self.display.blit(ship.RotatedSprite(), ship.xy) for ship in self.ships]
        [self.display.blit(bullet.RotatedSprite(), bullet.xy) for bullet in self.bullets]
        pygame.display.update()
                