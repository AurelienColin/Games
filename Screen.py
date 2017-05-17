from pygame.locals import *
from pytmx import *
import pyganim
from os.path import join
import pygame
import Map
import Highlight
import TextBox
import util
import Character
import Skill

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
        self._width = width
        self._height = height
        self._tile_size = tile_size
        self._animation_length = self._tile_size
        circle = pygame.image.load(join('res', 'sprite', 'circle.png'))
        self._objects = [[circle, (0, 0), 'hide']]
        self._portrait = False
        self._status = False
        self._status_box = -1
        self._ini_list = False
        self._childBox = False
        self._tile_effect = []

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
                ele, position, type_ele = element[:3]
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


    def onHover(self, pos):
        if self._portrait:
            for i in self._portrait:
                self.RemoveObject(i)
        mouse_pos = (pos[0]//self._tile_size, pos[1]//self._tile_size)
        for character in self._characters:
            if mouse_pos == character._pos_tile and not character._dead:
                pos = character._pos[0]+self._tile_size, character._pos[1]+self._tile_size
                self._portrait = self.AddTextBox(TextBox.Portrait(character), pos)
                print('Hovering on:', character, self._portrait)
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
        if box._imgs:
            for img in box._imgs:
                self._objects.append([img[0], (pos[0]+img[1][0], pos[1]+img[1][1]), 'sprite'])
        for i, text in enumerate(box._text):
            self._objects.append([text._string, (text._pos[0] + pos[0], text._pos[1] + pos[1]), 'text', text._text])
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


    def UpdateIniList(self, turns, turn):
        if self._ini_list:
            for i in self._ini_list:
                self.RemoveObject(i)
        self._ini_list = self.AddTextBox(TextBox.IniList(self._characters, turns, turn), (0, self._height-50))


    def MenuNavigation(self, key, menu_index, selection, selection_id):
        alpha = 80
        color = (0,0,0)
        self.RemoveObject(selection_id)
        if key == K_DOWN:
            selection = (selection+1)%len(menu_index)
            if selection == 0:
                selection +=1
        elif key == K_UP:
            selection = (selection-1)%len(menu_index)
            if selection == 0:
                selection = len(menu_index)-1
        if self._status_box!=-1 and len(self._objects[menu_index[selection]])>3:
            if self._childBox:
                for index in self._childBox:
                    self.RemoveObject(index)
            if self._objects[menu_index[selection]][3] in Skill.ListSkills():
                box = TextBox.SkillDetails(Skill.Skill.Initialization(self._objects[menu_index[selection]][3]))
            else:
                box = TextBox.ChildBox(self, self._objects[menu_index[selection]][3])
            self._childBox = self.AddTextBox(box,(self._height-128, self._width-2*100))
        height, width, pos_x, pos_y = util.ObjToCoord(self._objects[menu_index[selection]])
        s = Highlight.Highlight(width, height, alpha, color, pos_x, pos_y)
        selection_id = self.AddHighlight(s)
        return selection, selection_id


    def OpenMenu(self, key, character=None):
        text_box = TextBox.TextBox.Initialization(key, character=character, screen = self)
        pos_x = (self._height - text_box._height)/2
        pos_y = (self._width - text_box._width)/2
        self._menu_index = self.AddTextBox(text_box, (pos_x, pos_y))

        alpha = 80
        color = (0,0,0)
        height, width, pos_x, pos_y = util.ObjToCoord(self._objects[self._menu_index[1]])
        s = Highlight.Highlight(width, height, alpha, color, pos_x, pos_y)
        selection_id = self.AddHighlight(s)
        return self._menu_index, selection_id


    def QuitMenu(self, menu_index, selection_id):
        for i in menu_index:
            self.RemoveObject(i)
        self.RemoveObject(selection_id)


    def IniChar(self, characters):
        self._characters = []
        for character in characters:
            char = Character.Character.Initialization(character[0], self._tile_size, character[1], character[2], ia = character[3])
            char._index = self.AddCharacter(char, 'standing')
            self._characters.append(char)