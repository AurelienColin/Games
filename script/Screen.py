from pygame.locals import *
from pytmx import *
from os.path import join
import pygame
from . import Map, Highlight, TextBox, util, Character, Skill

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
        self.objects = [[circle, (0, 0), 'hide']]
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
        for element in self.objects:
            if element:
                ele, position, eleType = element[:3]
                if eleType == 'tiled_map':
                    # We add the circle after the map (and before anything else)
                    ele.draw(self.display)
                    if show != 'hide':
                        self.display.blit(circle, circle_pos)
                elif eleType == 'character':
                    ele.blit(self.display, position)
                elif eleType == 'box':
                    self.display.blit(ele.box, position)
                elif eleType != 'hide':
                    self.display.blit(ele, position)
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
        bar1Index = self.AddHighlight(character.lifebar[0])
        bar2Index = self.AddHighlight(character.lifebar[1])
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
                                      pos[1]+img[1][1]), 'sprite'])
        for i, text in enumerate(box.text):
            self.objects.append([text.string, (text.pixel[0] + pos[0],
                                                 text.pixel[1] + pos[1]),
                                 'text', text.text])
        return [i for i in range(prec-1, len(self.objects))]

    def AddHighlight(self, s):
        self.objects.append([s.content, (s.pixel[0], s.pixel[1]), 'highlight'])
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
            if self.objects[menuIndex[select]][3] in Skill.ListSkills():
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
