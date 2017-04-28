import pygame
import pyganim
from os.path import join
import Highlight

class Character():
    def __init__(self):
        self._sprite = {}
        self._cara = {}
        self.ini_cara()
        self._index = None
        self._lifebar1 = None
        self._lifebar2 = None
        self._pos = None
        self._skills = {}

    def ini_cara(self):
        self._cara['name'] = 'Anna'
        self._cara['sex'] = 'f'
        self._cara['PV'] = 20
        self._cara['PV_max'] = 100
        self._cara['PM'] = 4
        self._cara['PM_max'] = 4
        self._cara['PA'] = 6
        self._cara['PA_max'] = 6
        self._cara['vitesse'] = 100
        self._cara['attack'] = 100
        self._cara['defense'] = 100


    def AddSprite(self, key, sheet_file, rows, cols, begin, end):
        fullname = join('res', 'sprite', sheet_file)
        perso = pyganim.getImagesFromSpriteSheet(fullname,cols=cols,rows= rows)[begin:end]
        frames = list(zip(perso, [200]*(end-begin)))
        animObj = pyganim.PygAnimation(frames)
        animObj.play()
        self._sprite[key] = animObj

    def AddLifeBar(self, tile_size):
        width = 2
        percentage = self._cara['PV']/self._cara['PV_max']
        height_life = tile_size*percentage
        height_void = tile_size - height_life
        if percentage < 0.5:
            R = 255
            G = 255 - 255*(1-percentage*2)
        else:
            R = 255*(1-percentage)*2
            G = 255
        B = 0
        print(R,G,B)
        self._lifebar1 = Highlight.Highlight(height_life, width, 255, (R, G, B), self._pos[0], self._pos[1])
        self._lifebar2 = Highlight.Highlight(height_void, width, 255, (0, 0, 0), self._pos[0]+height_life, self._pos[1])
