# -*- coding: utf-8 -*-
"""
Created on Thu Jul  5 18:00:07 2018

@author: Rignak
"""

from TacticalWarship import Screen
import pygame

from os.path import join

def Launcher():
    pygame.init()
    global screenDim
    screenDim = (1000,1000)
    background = pygame.image.load(join('res', 'img', 'bg_main.png'))
    screen = Screen.Screen(screenDim, background)
    
    return screen
    
if __name__ == '__main__':
    screen = Launcher()
    screen.Refresh()