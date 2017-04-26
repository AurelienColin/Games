import pygame

class Highlight():
    def __init__(self, height, width, alpha, color, pos_x, pos_y):
        s = pygame.Surface((height, width))
        s.fill(color)
        s.set_alpha(alpha)
        self._content = s
        self._pos_x = pos_x
        self._pos_y = pos_y
