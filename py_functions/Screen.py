from pygame.locals import *
from pytmx import *
from os.path import join
import pygame
import pyganim
from . import Map, Highlight, TextBox, util, Character, Skill, Item
from .Loop import listSkills
from .TextBox import itemList

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
        circle = pygame.image.load(join('res', 'sprite', 'others', 'circle.png'))
        self.objects = [[circle, (-tileSize, -tileSize), 'hide']]
        self.charBox = -1
        self.ui={'hovering':[],'initiative':[], 'childBox':[]}
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
        box = [obj[:4] for obj in self.objects if obj and obj[2]=='box']
        highlight = [obj[:2] for obj in self.objects if obj and obj[2] == 'highlight']

        [ele[0].draw(self.display) for ele in tiled_map]
        if show!='hide':
            self.display.blit(circle, circle_pos)

        tiles = [effect[0] for effect in self.tileEffects]
        white = Highlight.HighlightTiles(self.tileSize,tiles, 120, (255, 255,255))
        [self.display.blit(tile.content, tile.pixel) for tile in white.values()]
        [ele.blit(self.display, pos) for ele, pos in characters]
        [self.display.blit(ele, pos) for ele, pos in sprites]
        for ele, pos, t, index in box:
            for i in index:
                ele2, pos2=  self.objects[i][:2]
                if type(ele2) == pygame.Surface:
                    self.display.blit(ele2, pos2)
                elif type(ele2) != pyganim.PygAnimation :
                    for j in range(len(ele2.box)):
                        self.display.blit(ele2.box[j], ele2.pos[j])
        [self.display.blit(ele, pos) for ele, pos in highlight]

        pygame.display.update()

    def Clean(self):
        circle = pygame.image.load(join('res', 'sprite', 'others', 'circle.png'))
        self.objects = [[circle, (0, 0), 'hide']]
        self.ui={'hovering':[], 'initiative':[], 'status':[], 'childBox':[]}
        self.charBox = -1


    def onHover(self, pos):
        for i in self.ui['hovering']:
            self.RemoveObject(i)
        mouse_pos = (pos[0]//self.tileSize, pos[1]//self.tileSize)
        for character in self.characters:
            if mouse_pos == character.pos['tile']:
                pos = character.pos['px'][0]+self.tileSize, character.pos['px'][1]+self.tileSize
                self.ui['hovering'] = self.AddTextBox(TextBox.Portrait(character, [pos]))
                break
        box = TextBox.TileData(mouse_pos,self.mapData, self.tileSize, [(self.size[0]-90,0)])
        self.ui['hovering'] += self.AddTextBox(box)
        return mouse_pos

    def RemoveObject(self, index):
        self.objects[index] = None

    def AddSprite(self, sprite, pos):
        if str(type(sprite))=="<class 'pyganim.PygAnimation'>":
            self.objects.append([sprite, pos, 'character'])
        else:
            self.objects.append([sprite, pos, 'sprite'])
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

    def AddTextBox(self, box):
        prec = len(self.objects)
        self.objects.append([box, box.pos[0], 'box'])
        if box.imgs:
            for img in box.imgs:
                self.objects.append([img[0], (box.pos[0][0]+img[1][0],
                                     box.pos[0][1]+img[1][1]), 'others'])
        for i, text in enumerate(box.text):
            self.objects.append([text.string, (text.pixel[0] + box.pos[0][0],
                                                 text.pixel[1] + box.pos[0][1]),
                                 'text', text.text])
        index = [i for i in range(prec, len(self.objects))]
        self.objects[prec].append(index)
        return index

    def AddHighlight(self, s, priority=True):
        if priority:
            self.objects.append([s.content, (s.pixel[0], s.pixel[1]), 'highlight'])
        else:
            self.objects.append([s.content, (s.pixel[0], s.pixel[1]), 'sprite'])
        return len(self.objects)-1

    def UpdateStatus(self, character, pos=False):
        pos = [(self.size[1]-128, self.size[0]-100)]
        for i in self.ui['status']:
            self.RemoveObject(i)
        self.ui['status'] = self.AddTextBox(TextBox.Status(character, pos))


    def UpdateIniList(self, turns, turn):
        for i in self.ui['initiative']:
            self.RemoveObject(i)
        box = TextBox.IniList(self.characters, turns, turn, [(0, self.size[1]-50)])
        self.ui['initiative'] = self.AddTextBox(box)


    def MenuNavigation(self, key, menuIndex, select, selectId):
        alpha = 80
        color = (0,0,0)
        self.RemoveObject(selectId)
        pos = [(self.size[0]-128, self.size[1]-2*100)]
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
            name = self.objects[menuIndex[select]][3]
            if [skill for skill in listSkills() if skill in name]:
                skillName = [skill for skill in listSkills() if skill in name][0]
                box = TextBox.SkillDetails(Skill.Skill(skillName),
                                           self.characters[self.charBox], pos)
            elif [item for item in itemList() if item in name]:
                itemName = [item for item in itemList() if item in name][0]
                pos = [(pos[0][0], pos[0][1]-170)]
                box = TextBox.ItemDetails(Item.Item(itemName), pos)
            else:
                box = TextBox.ChildBox(name, pos)
            self.ui['childBox'] = self.AddTextBox(box)
        size, pos = util.ObjToCoord(self.objects[menuIndex[select]])
        s = Highlight.Highlight(size, alpha, color, pos)
        selectId = self.AddHighlight(s)
        return select, selectId


    def OpenMenu(self, key, char=None):
        box = TextBox.TextBox.Initialization(key, ['middle', self.size], char=char, screen = self)
        self.menuIndex = self.AddTextBox(box)

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
                                        coef=character['coef'],
                                        level=character['level'],
                                        items=character['items'])
            if character['initial']!=[-1,-1]:
                char.index = self.AddCharacter(char, 'standing')
            self.characters.append(char)

    def RemoveUI(self):
        for index in self.ui['childBox'] + self.ui['hovering']:
            self.RemoveObject(index)
        self.ui['childBox'] = []
        self.ui['hovering'] = []
