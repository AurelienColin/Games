from pygame.locals import *
from pytmx import *
from os.path import join
import pygame
from . import Map, Highlight, TextBox, util, Character, Skill
from .Loop import listSkills

class Screen():
    """A screen had
    - a pygame.display
    - a tileSize (since it's constituted by square
    - a list of objects, which are tuple of
        [0] : the actual object
        [1] : the coordinates (a tuple of int)
        [2] ; its type (sprite, map, or anything else), a string"""
    def __init__(self, width, height, tileSize):
        self.size = (width, height)
        self.display = pygame.display.set_mode(self.size, pygame.RESIZABLE)
        self.tileSize = tileSize
        self.frameNumber = self.tileSize
        circle = pygame.image.load(join('res', 'sprite', 'circle.png'))
        self.objects = [[circle, (-tileSize, -tileSize), 'hide']]
        self.charBox = -1
        self.ui={'hovering':[],'initiative':[]}
        self.tileEffects = []

    def MoveCircle(self, pos = None, hide = False):
        if hide:
            self.objects[0][2] = 'hide'
        else:
            self.objects[0][1] = pos
            self.objects[0][2] = 'show'

    def refresh(self):
        circle, circle_pos, show = self.objects[0]
        circle_pos = (circle_pos[0]-4, circle_pos[1])
        tiled_map = [obj[:2] for obj in self.objects if obj and obj[2]=='tiled_map']
        characters = [obj[:2] for obj in self.objects if obj and obj[2]=='character']
        sprites = [obj[:2] for obj in self.objects if obj and obj[2]=='sprite']
        box = [obj[:2] for obj in self.objects if obj and obj[2]=='box']
        others = [obj[:2] for obj in self.objects if obj and obj[2] not in ['tiled_map','hide',
                                                              'character', 'box', 'sprite', 'show']]

        [ele[0].draw(self.display) for ele in tiled_map]
        if show!='hide':
            self.display.blit(circle, circle_pos)

        tiles = [effect[0] for effect in self.tileEffects]
        white = Highlight.HighlightTiles(self.tileSize,tiles, 120, (255, 255,255))
        [self.display.blit(tile.content, tile.pixel) for tile in white.values()]
        [ele.blit(self.display, pos) for ele, pos in characters]
        [self.display.blit(ele, pos) for ele, pos in sprites]
        [self.display.blit(ele.box, pos) for ele, pos in box]
        [self.display.blit(ele, pos) for ele, pos in others]

        pygame.display.update()

    def Clean(self):
        circle = pygame.image.load(join('res', 'sprite', 'circle.png'))
        self.objects = [[circle, (0, 0), 'hide']]
        self.ui={'hovering':[], 'initiative':[], 'status':[], 'childBox':[]}
        self.charBox = -1


    def onHover(self, pos):
        for i in self.ui['hovering']:
            self.RemoveObject(i)
        mouse_pos = (pos[0]//self.tileSize, pos[1]//self.tileSize)
        for character in self.characters:
            if mouse_pos == character.pos['tile'] and not character.dead:
                pos = character.pos['px'][0]+self.tileSize, character.pos['px'][1]+self.tileSize
                self.ui['hovering'] = self.AddTextBox(TextBox.Portrait(character), pos)
                break
        box = TextBox.TileData(mouse_pos,self.mapData, self.tileSize)
        self.ui['hovering'] += self.AddTextBox(box, (self.size[0]-90,0))
        return mouse_pos

    def RemoveObject(self, index):
        self.objects[index] = None

    def AddSprite(self, sprite, pos):
        if str(type(sprite))=="<class 'pyganim.PygAnimation'>":
            self.objects.append([sprite, pos, 'character'])
        else:
            self.objects.append([sprite, pos, 'sprite'])
        print('add sprite at:', pos)
        return len(self.objects)-1

    def AddCharacter(self, character, key):
        """The len is returned to know where is the sprite"""
        sprite = character.sprite[key]
        self.objects.append([sprite, character.pos['px'], 'character'])
        bar1Index = self.AddHighlight(character.lifebar[0], priority=False)
        bar2Index = self.AddHighlight(character.lifebar[1], priority=False)
        return bar1Index-1, bar1Index, bar2Index

    def AddMap(self, filename):
        fullname = join('res', 'map', filename)
        self.objects.append([Map.TiledMap(fullname), (0, 0), 'tiled_map'])
        self.objects[-1][0].run(self)
        return len(self.objects)-1

    def AddTextBox(self, box, pos):
        self.objects.append([box, pos, 'box'])
        prec = len(self.objects)
        if box.imgs:
            for img in box.imgs:
                self.objects.append([img[0], (pos[0]+img[1][0],
                                      pos[1]+img[1][1]), 'others'])
        for i, text in enumerate(box.text):
            self.objects.append([text.string, (text.pixel[0] + pos[0],
                                                 text.pixel[1] + pos[1]),
                                 'text', text.text])
        return [i for i in range(prec-1, len(self.objects))]

    def AddHighlight(self, s, priority=True):
        if priority:
            self.objects.append([s.content, (s.pixel[0], s.pixel[1]), 'highlight'])
        else:
            self.objects.append([s.content, (s.pixel[0], s.pixel[1]), 'sprite'])
        return len(self.objects)-1

    def UpdateStatus(self, character, pos=False):
        pos = (self.size[1]-128, self.size[0]-100)
        for i in self.ui['status']:
            self.RemoveObject(i)
        self.ui['status'] = self.AddTextBox(TextBox.Status(character), pos)


    def UpdateIniList(self, turns, turn):
        for i in self.ui['initiative']:
            self.RemoveObject(i)
        box = TextBox.IniList(self.characters, turns, turn)
        self.ui['initiative'] = self.AddTextBox(box, (0, self.size[1]-50))


    def MenuNavigation(self, key, menuIndex, select, selectId):
        alpha = 80
        color = (0,0,0)
        self.RemoveObject(selectId)
        if key == K_DOWN:
            select = (select+1)%len(menuIndex)
            if select == 0:
                select +=1
        elif key == K_UP:
            select = (select-1)%len(menuIndex)
            if select == 0:
                select = len(menuIndex)-1
        if self.charBox!=-1 and len(self.objects[menuIndex[select]])>3:
            for i in self.ui['childBox']:
                    self.RemoveObject(i)
            if self.objects[menuIndex[select]][3] in listSkills():
                box = TextBox.SkillDetails(Skill.Skill(self.objects[menuIndex[select]][3]),
                                           self.characters[self.charBox])
            else:
                box = TextBox.ChildBox(self.objects[menuIndex[select]][3])
            self.ui['childBox'] = self.AddTextBox(box,(self.size[0]-128, self.size[1]-2*100))
        size, pos = util.ObjToCoord(self.objects[menuIndex[select]])
        s = Highlight.Highlight(size, alpha, color, pos)
        selectId = self.AddHighlight(s)
        return select, selectId


    def OpenMenu(self, key, char=None):
        box = TextBox.TextBox.Initialization(key, char=char, screen = self)
        posX = (self.size[0] - box.size[0])/2
        posY = (self.size[1] - box.size[1])/2
        self.menuIndex = self.AddTextBox(box, (posX, posY))

        alpha = 80
        color = (0,0,0)
        size, pos = util.ObjToCoord(self.objects[self.menuIndex[1]])
        s = Highlight.Highlight(size, alpha, color, pos)
        selectId = self.AddHighlight(s)
        return self.menuIndex, selectId


    def QuitMenu(self, menuIndex, selectId):
        for i in menuIndex:
            self.RemoveObject(i)
        self.RemoveObject(selectId)

    def IniChar(self, characters):
        self.characters = []
        for character in characters:
            char = Character.Character(character['name'], character['team'],
                                       tileSize = self.tileSize,
                                       posTile = character['initial'],
                                        ia = character['ia'],
                                        leader = character['leader'],
                                        coef=character['coef'])
            if character['initial']:
                char.index = self.AddCharacter(char, 'standing')
            self.characters.append(char)
