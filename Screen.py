from pygame.locals import *
from pytmx import *
import pyganim
from os.path import join
import pygame
import Map
import Highlight
import TextBox

class Screen():
    """A screen had
    - a pygame.display
    - a tile_size (since it's constituted by square
    - a list of objects, which are tuple of
        [0] : the actual object
        [1] : the coordinates (a tuple of int)
        [2] ; its type (sprite, map, or anything else), a string"""
    def __init__(self, width, height, tile_size):
        self._display = pygame.display.set_mode((width, height), pygame.RESIZABLE)
        self._tile_size = tile_size
        self._objects = []

    def refresh(self):
        for element in self._objects:
            if element:
                ele, position, type_ele = element
                if type_ele == 'tiled_map':
                    ele.draw(self._display)
                elif type_ele == 'sprite':
                    ele.blit(self._display, position)
                else:
                    self._display.blit(ele, position)
        pygame.display.update()

    def RemoveObject(self, index):
        self._objects[index] = None

    def AddSprite(self, sheet_file, pos_x = 0, pos_y = 0, rows=1, cols=1, begin = 0, end = -1):
        """The len is returned to know where is the sprite"""
        fullname = join('res', 'sprite', sheet_file)
        perso = pyganim.getImagesFromSpriteSheet(fullname,cols=cols,rows= rows)[begin:end]
        frames = list(zip(perso, [200]*(end-begin)))
        animObj = pyganim.PygAnimation(frames)
        animObj.play()
        self._objects.append([animObj, (pos_x, pos_y), 'sprite'])
        return len(self._objects)-1

    def AddMap(self, filename):
        fullname = join('res', 'map', filename)
        self._objects.append([Map.TiledMap(fullname), (0, 0), 'tiled_map'])
        self._objects[-1][0].run(self)
        return len(self._objects)-1

    def AddTextBox(self, box, pos_x = 0, pos_y = 0):
        self._objects.append([box._box, (pos_x, pos_y), 'box'])
        prec = len(self._objects)
        for text in box._text:
            self._objects.append([text._string, (text._pos_x + pos_x, text._pos_y + pos_y), 'text'])
        return [i for i in range(prec-1, len(self._objects))]

    def AddHighlight(self, height, width, alpha, color, pos_x, pos_y):
        s = Highlight.Highlight(height, width, alpha, color, pos_x, pos_y)
        self._objects.append([s._content, (s._pos_x, s._pos_y), 'highlight'])
        return len(self._objects)-1
