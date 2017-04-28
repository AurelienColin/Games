import pygame
from os.path import join

class TextBox():
    def __init__(self, box_file, text, height=0, width=0, pos_x = 0, pos_y = 0, size = 20):
        fullname = join('res', 'textbox', box_file)
        self._string = text.split('\n')
        self._text = [Text(self._string[i], pos_x, pos_y+i*20, 20) for i in range(len(self._string))]
        if height == 0 or width == 0:
            self._box =  pygame.image.load(fullname)
        else:
            img = pygame.image.load(fullname)
            self._box = pygame.transform.smoothscale(img, (width, height))

class Text():
    def __init__(self, text, pos_x, pos_y, size):
        font = pygame.font.SysFont('freesans', size)
        self._string = font.render(text, True, (0,0,0))
        self._pos_x = pos_x
        self._pos_y = pos_y
