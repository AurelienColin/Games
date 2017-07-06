import pygame

class Highlight():
    def __init__(self, size, alpha, color, pos):
        s = pygame.Surface(size)
        s.fill(color)
        s.set_alpha(alpha)
        self._content = s
        self._pixel = pos

def HighlightTiles(tile_size, tiles, alpha, color):
    highlighted = {}
    size = (tile_size, tile_size)
    for tile in tiles:
        pos = (tile[0]*tile_size, tile[1]*tile_size)
        highlighted[tuple(tile)] = Highlight(size, alpha, color,pos)
    return highlighted
