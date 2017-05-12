import pygame
from os.path import join

class TextBox():
    def __init__(self, box_file, text, height, width, pos, size=20):
        fullname = join('res', 'textbox', box_file)
        self._string = text.split(';')
        self._text = [Text(self._string[i], (pos[0], pos[1]+i*size), 20) for i in range(len(self._string))]
        self._height = height
        self._width = width
        self._img = False
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
        self._img = [character._portrait, (0, size[1]-128-12)]

def ListMenus():
    return set(['MainMenu', 'Skills'])