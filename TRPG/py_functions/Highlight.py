import pygame

class Highlight():
    def __init__(self, size, alpha, color, pos):
        s = pygame.Surface(size)
        s.fill(color)
        s.set_alpha(alpha)
        self.content = s
        self.pixel = pos

def HighlightTiles(tileSize, tiles, alpha, color):
    highlighted = {}
    size = (tileSize, tileSize)
    for tile in tiles:
        pos = (tile[0]*tileSize, tile[1]*tileSize)
        highlighted[tuple(tile)] = Highlight(size, alpha, color,pos)
    return highlighted
