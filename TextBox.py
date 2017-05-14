import pygame
from os.path import join
import util

class TextBox():
    def __init__(self, box_file, text, height, width, pos, size=20):
        fullname = join('res', 'textbox', box_file)
        self._string = text.split(';')
        self._text = [Text(self._string[i], (pos[0], pos[1]+i*size), 20) for i in range(len(self._string))]
        self._height = height
        self._width = width
        self._imgs = False
        img = pygame.image.load(fullname)
        self._box = pygame.transform.smoothscale(img, (height, width))

    def Initialization(name, character=None):
        if name == 'MainMenu':
            self = MainMenu()
        elif name == 'Skills':
            self = SkillMenu(character)
        else:
            self = None
        return self

class Text():
    def __init__(self, text, pos, size):
        font = pygame.font.SysFont('freesans', size)
        self._string = font.render(text, True, (0,0,0))
        self._pos = pos

class MainMenu(TextBox):
    def __init__(self):
        string = "Aide;Skills;Objets;Status;Exit;End Turn"
        name = "TextBox_ExtraLarge.png"
        TextBox.__init__(self,name, string, 130, 170, (30, 20))

class SkillMenu(TextBox):
    def __init__(self, character):
        skills = [skill._name for skill in character._skills]
        string = ';'.join(skills)
        name = "TextBox_ExtraLarge.png"
        TextBox.__init__(self, name, string, 150, 150, (30, 30))

class Status(TextBox):
    def __init__(self, character):
        data = [str(character._cara['name']),
                'PV: '+ str(character._cara['PV']) + '/' + str(character._cara['PV_max']),
                'PA: '+ str(character._cara['PA']) + '/' + str(character._cara['PA_max']),
                'PM: '+ str(character._cara['PM']) + '/' + str(character._cara['PM_max'])]
        string = ';'.join(data)
        name = "TextBox_ExtraLarge.png"
        TextBox.__init__(self, name, string, 128, 100, (20, 10))

    def Update(self, character):
        data = [str(character._cara['name']),
                'PV: '+ str(character._cara['PV']) + '/' + str(character._cara['PV_max']),
                'PA: '+ str(character._cara['PA']) + '/' + str(character._cara['PA_max']),
                'PM: '+ str(character._cara['PM']) + '/' + str(character._cara['PM_max'])]
        text = ';'.join(data)
        self._string = text.split(';')

class SkillDetails(TextBox):
    def __init__(self, skill):
        data = [skill._name, 'Type: ' + skill._type, 'PA: ' + str(skill._cost), 'Dmg: ' + str(skill._damage)]
        string =';'.join(data)
        name = "TextBox_ExtraLarge.png"
        TextBox.__init__(self, name, string, 128, 100, (20, 10))

class Portrait(TextBox):
    def __init__(self, character):
        size = 128, 230
        data = [str(character._cara['name']),
                'PV: '+ str(character._cara['PV']) + '/' + str(character._cara['PV_max']),
                'PA: '+ str(character._cara['PA']) + '/' + str(character._cara['PA_max']),
                'PM: '+ str(character._cara['PM']) + '/' + str(character._cara['PM_max'])]
        string = ';'.join(data)
        name = "TextBox_ExtraLarge.png"
        TextBox.__init__(self, name, string, size[0], size[1], (20, 10))
        self._imgs = [[character._portrait, (0, size[1]-128-12)]]

class IniList(TextBox):
    def __init__(self, characters, turns, turn):
        temp_turns, i, j, temp = turns, turn, 0, []
        cap = 10
        margin = 37
        while j < len(characters)*2:
            if i in temp_turns:
                j+=1
                temp.append(temp_turns[i])
                k = turn + int(util.StatCalculation(turns[turn]._cara['speed'])*100)
                while k in temp_turns:
                    k+=1
                temp_turns[k] = temp_turns[i]
            i += 1
        size = margin*min(cap, len(characters)*2)+10, 50
        name = "TextBox_LongSmall.png"
        TextBox.__init__(self, name, '', size[0], size[1], (0, 0))
        self._imgs = []
        for i, character in enumerate(temp):
            self._imgs.append([character._sprite['static'], (5+i*margin, 10)])
            if i == cap:
                break


def ListMenus():
    return set(['MainMenu', 'Skills'])