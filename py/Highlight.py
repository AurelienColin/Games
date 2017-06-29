import pygame

class Highlight():
    def __init__(self, height, width, alpha, color, pos_x, pos_y):
        s = pygame.Surface((height, width))
        s.fill(color)
        s.set_alpha(alpha)
        self._content = s
        self._pixel = pos_x, pos_y

def HighlightTiles(tile_size, tiles, alpha, color):
    highlighted = {}
    if type(tiles) == list:
        for x, y in tiles:
            highlighted[(x, y)] = Highlight(tile_size, tile_size, alpha, color,
                                         x*tile_size, y*tile_size)
    else:
        highlighted[tiles] = Highlight(tile_size, tile_size, alpha, color,
                                       tiles[0]*tile_size, tiles[1]*tile_size)

    return highlighted
