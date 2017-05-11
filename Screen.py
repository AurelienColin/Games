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

        circle = pygame.image.load(join('res', 'sprite', 'circle.png'))
        self._objects = [[circle, (0, 0), 'hide']]
        self._portrait = False
        self._status = False

    def MoveCircle(self, pos = None, hide = False):
        if hide:
            self._objects[0][2] = 'hide'
        else:
            self._objects[0][1] = pos
            self._objects[0][2] = 'show'

    def refresh(self):
        circle, circle_pos, show = self._objects[0]
        circle_pos = (circle_pos[0]-4, circle_pos[1])
        for element in self._objects:
            if element:
                ele, position, type_ele = element
                if type_ele == 'tiled_map':
                    ele.draw(self._display)
                    if show != 'hide':
                        self._display.blit(circle, circle_pos)
                elif type_ele == 'character':
                    ele.blit(self._display, position)
                elif type_ele == 'box':
                    self._display.blit(ele._box, position)
                elif type_ele != 'hide':
                    self._display.blit(ele, position)
        pygame.display.update()

    def SetCharacters(self, teams):
        self._characters = []
        for team in teams:
            for character in team._members:
                self._characters.append(character)

    def onHover(self, pos):
        if self._portrait:
            for i in self._portrait:
                self.RemoveObject(i)
        mouse_pos = (pos[0]//self._tile_size, pos[1]//self._tile_size)
        for character in self._characters:
            if mouse_pos == character._pos_tile and not character._dead:
                pos = character._pos[0]+self._tile_size, character._pos[1]+self._tile_size
                self._portrait = self.AddTextBox(TextBox.Portrait(character), pos)
                print('Hovering on:', character)
                print(self._portrait)
                return

    def RemoveObject(self, index):
        self._objects[index] = None

    def AddSprite(self, sprite, pos):
        self._objects.append([sprite, pos, 'sprite'])
        return len(self._objects)-1

    def AddCharacter(self, character, key):
        """The len is returned to know where is the sprite"""
        sprite = character._sprite[key]
        self._objects.append([sprite, character._pos, 'character'])
        bar1_index = self.AddHighlight(character._lifebar1)
        bar2_index = self.AddHighlight(character._lifebar2)
        return bar1_index-1, bar1_index, bar2_index

    def AddMap(self, filename):
        fullname = join('res', 'map', filename)
        self._objects.append([Map.TiledMap(fullname), (0, 0), 'tiled_map'])
        self._objects[-1][0].run(self)
        return len(self._objects)-1

    def AddTextBox(self, box, pos):
        self._objects.append([box, pos, 'box'])
        prec = len(self._objects)
        if box._img:
            self._objects.append([box._img[0], (pos[0]+box._img[1][0], pos[1]+box._img[1][1]), 'sprite'])
        for text in box._text:
            self._objects.append([text._string, (text._pos[0] + pos[0], text._pos[1] + pos[1]), 'text'])
        return [i for i in range(prec-1, len(self._objects))]

    def AddHighlight(self, s):
        self._objects.append([s._content, (s._pos[0], s._pos[1]), 'highlight'])
        return len(self._objects)-1

    def UpdateStatus(self, character, pos=False):
        if pos:
            self._status = self.AddTextBox(TextBox.Status(character), pos)
        elif self._status:
            pos = self._objects[self._status[0]][1]
            for i in self._status:
                self.RemoveObject(i)
            self._status = self.AddTextBox(TextBox.Status(character), pos)