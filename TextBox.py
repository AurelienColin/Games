import pygame
from os.path import join

class TextBox():
    def __init__(self, box_file, text, height, width, pos, size=20):
        fullname = join('res', 'textbox', box_file)
        self._string = text.split(';')
        self._text = [Text(self._string[i], (pos[0], pos[1]+i*size), 20) for i in range(len(self._string))]
        self._height = height
        self._width = width

        img = pygame.image.load(fullname)
        self._box = pygame.transform.smoothscale(img, (width, height))

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
        string = "Aide;Skills;Objets;Status;Exit"
        name = "TextBox_ExtraLarge.png"
        TextBox.__init__(self,name, string, 150, 100, (30, 20))

class SkillMenu(TextBox):
    def __init__(self, character):
        skills = [skill._name for skill in character._skills]
        string = ';'.join(skills)
        name = "TextBox_ExtraLarge.png"
        TextBox.__init__(self, name, string, 150, 150, (30, 30))


def ListMenus():
    return set(['MainMenu', 'Skills'])