from pygame.locals import *
from pytmx import *
from os.path import join
import pygame
from . import Map, Highlight, TextBox, util, Character, Skill

class Screen():
    """A screen had
    - a pygame.display
    - a tile_size (since it's constituted by square
    - a list of objects, which are tuple of
        [0] : the actual object
        [1] : the coordinates (a tuple of int)
        [2] ; its type (sprite, map, or anything else), a string"""
    def __init__(self, width, height, tile_size):
        self._size = (width, height)
        self._display = pygame.display.set_mode(self._size, pygame.RESIZABLE)
        self._tile_size = tile_size
        self._animation_length = self._tile_size
        circle = pygame.image.load(join('res', 'sprite', 'circle.png'))
        self._objects = [[circle, (0, 0), 'hide']]
        self._charBox = -1
        self._ui={'hovering':[],'initiative':[]}

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
                    # We add the circle after the map (and before anything else)
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

    def Clean(self):
        circle = pygame.image.load(join('res', 'sprite', 'circle.png'))
        self._objects = [[circle, (0, 0), 'hide']]
        self._ui={'hovering':[], 'initiative':[], 'status':[], 'childBox':[]}
        self._charBox = -1


    def onHover(self, pos):
        for i in self._ui['hovering']:
            self.RemoveObject(i)
        mouse_pos = (pos[0]//self._tile_size, pos[1]//self._tile_size)
        for character in self._characters:
            if mouse_pos == character._tile and not character._dead:
                pos = character._pixel[0]+self._tile_size, character._pixel[1]+self._tile_size
                self._ui['hovering'] = self.AddTextBox(TextBox.Portrait(character), pos)
                break
        box = TextBox.TileData(mouse_pos,self._map_data, self._tile_size)
        self._ui['hovering'] += self.AddTextBox(box, (self._size[0]-90,0))
        return mouse_pos

    def RemoveObject(self, index):
        self._objects[index] = None

    def AddSprite(self, sprite, pos):
        if str(type(sprite))=="<class 'pyganim.PygAnimation'>":
            self._objects.append([sprite, pos, 'character'])
        else:
            self._objects.append([sprite, pos, 'sprite'])
        print('add sprite at:', pos)
        return len(self._objects)-1

    def AddCharacter(self, character, key):
        """The len is returned to know where is the sprite"""
        sprite = character._sprite[key]
        self._objects.append([sprite, character._pixel, 'character'])
        bar1_index = self.AddHighlight(character._lifebar[0])
        bar2_index = self.AddHighlight(character._lifebar[1])
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
                self._objects.append([img[0], (pos[0]+img[1][0],
                                      pos[1]+img[1][1]), 'sprite'])
        for i, text in enumerate(box._text):
            self._objects.append([text._string, (text._pixel[0] + pos[0],
                                                 text._pixel[1] + pos[1]),
                                 'text', text._text])
        return [i for i in range(prec-1, len(self._objects))]

    def AddHighlight(self, s):
        self._objects.append([s._content, (s._pixel[0], s._pixel[1]), 'highlight'])
        return len(self._objects)-1

    def UpdateStatus(self, character, pos=False):
        pos = (self._size[1]-128, self._size[0]-100)
        for i in self._ui['status']:
            self.RemoveObject(i)
        self._ui['status'] = self.AddTextBox(TextBox.Status(character), pos)


    def UpdateIniList(self, turns, turn):
        for i in self._ui['initiative']:
            self.RemoveObject(i)
        box = TextBox.IniList(self._characters, turns, turn)
        self._ui['initiative'] = self.AddTextBox(box, (0, self._size[1]-50))


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
        if self._charBox!=-1 and len(self._objects[menu_index[selection]])>3:
            for i in self._ui['childBox']:
                    self.RemoveObject(i)
            if self._objects[menu_index[selection]][3] in Skill.ListSkills():
                box = TextBox.SkillDetails(Skill.Skill(self._objects[menu_index[selection]][3]),
                                           self._characters[self._charBox])
            else:
                box = TextBox.ChildBox(self._objects[menu_index[selection]][3])
            self._ui['childBox'] = self.AddTextBox(box,(self._size[0]-128, self._size[1]-2*100))
        size, pos = util.ObjToCoord(self._objects[menu_index[selection]])
        s = Highlight.Highlight(size, alpha, color, pos)
        selection_id = self.AddHighlight(s)
        return selection, selection_id


    def OpenMenu(self, key, character=None):
        text_box = TextBox.TextBox.Initialization(key, character=character, screen = self)
        pos_x = (self._size[0] - text_box._size[0])/2
        pos_y = (self._size[1] - text_box._size[1])/2
        self._menu_index = self.AddTextBox(text_box, (pos_x, pos_y))

        alpha = 80
        color = (0,0,0)
        size, pos = util.ObjToCoord(self._objects[self._menu_index[1]])
        s = Highlight.Highlight(size, alpha, color, pos)
        selection_id = self.AddHighlight(s)
        return self._menu_index, selection_id


    def QuitMenu(self, menu_index, selection_id):
        for i in menu_index:
            self.RemoveObject(i)
        self.RemoveObject(selection_id)

    def IniChar(self, characters):
        self._characters = []
        for character in characters:
            char = Character.Character(character['name'], character['team'],
                                       tile_size = self._tile_size,
                                       pos_tile = character['initial'],
                                        ia = character['ia'],
                                        leader = character['leader'],
                                        coef=character['coef'])
            if character['initial']:
                char._index = self.AddCharacter(char, 'standing')
            self._characters.append(char)
