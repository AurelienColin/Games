import pygame

class Highlight():
    def __init__(self, height, width, alpha, color, pos_x, pos_y):
        s = pygame.Surface((height, width))
        s.fill(color)
        s.set_alpha(alpha)
        self._content = s
        self._pos = pos_x, pos_y

def HighlightTiles(tile_size, tiles, alpha, color):
    highlighted = {}
    for pos in tiles:
        highlighted[pos] = Highlight(tile_size, tile_size, alpha, color,
                                     pos[0]*tile_size, pos[1]*tile_size)
    return highlighted