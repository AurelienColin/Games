# -*- coding: utf-8 -*-
"""
Created on Sun Jul  8 14:28:40 2018

@author: Rignak
"""
import pygame
from os.path import join

#Imported for performance
from pygame.transform import rotate
from pygame.mask import from_surface

class Sprite():
    def __init__(self, name, xy):
        self.origSprite = pygame.image.load(join('res', 'img', name))
        self.image = self.origSprite
        self.rect = self.image.get_rect()
        self.rect.center = xy
        self.mask = from_surface(self.image)

    def Rotate(self, angle):
        self.image = rotate(self.origSprite, angle)
        self.mask = from_surface(self.image)
        x, y = self.rect.center  # Save its current center.
        self.rect = self.image.get_rect()  # Replace old rect with new rect.
        self.rect.center = (x, y)  # Put the new rect's center at old center.

    def Move(self):
        x,y = self.rect.center
        if self.speed[0]:
            x += self.speed[0]
        if self.speed[1]:
            y += self.speed[1]
        if self.speed[2]:
            self.angle = (self.angle+self.speed[2])%360
        self.rect.center = (x, y)
