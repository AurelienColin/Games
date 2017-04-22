"""
This is tested on pygame 1.9 and python 2.7 and 3.3+.
Leif Theden "bitcraft", 2012-2014

Rendering demo for the TMXLoader.

Typically this is run to verify that any code changes do do break the loader.
Tests all Tiled features -except- terrains and object rotation.

If you are not familiar with python classes, you might want to check the
'tutorial' app.

Missing tests:
- object rotation
"""
import sys
import pygame
from pygame.locals import *
from pytmx import *
from pytmx.util_pygame import load_pygame
import pyganim
import logging
from os.path import join

logger = logging.getLogger(__name__)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
logger.addHandler(ch)
logger.setLevel(logging.INFO)

#Each class will later be in a different file

class Character():
    def __init__(self):
        self._name = "Anna"
        self._class = 'Aventurier'
        self._sex = 'f'
        self._niveau = 1
        self._PV = 100
        self._sprite_sheet = "Res\\63468.png"
        self._maxPA = 6
        self._PA = self._maxPA
        self._maxPM = 4
        self._PM = self._maxPM
        self._active_skills = [Skill()]
        self._passive_skills = []
        self._XP = 0
        self._effects = []

    def UsePM(self, slowness):
        if slowness < self._PM:
            self._PM -= slowness
            return True
        else:
            return False

    def UsePA(self, cost):
        if cost < self._PA:
            self._PA -= cost
            return True
        else:
            return False

    def NewTurn(self):
        self._PA = self._maxPA
        self._PM = self._maxPM

# The skills will be later wroten in XML
class Skill():
    def __init__(self):
        self._name = 'Horizontal'
        self._AOE = 'parallel'
        self._size = 3
        self._cost = 4
        self._sprite_sheet = ''
        self._effects = []


class Screen():
    """A screen had
    - a pygame.display
    - a tile_size (since it's constituted by square
    - a list of objects, which are tuple of
        [0] : the actual object
        [1] : the coordinates (a tuple of int)
        [2] ; its type (sprite, map, or anything else), a string"""
    def __init__(self, width, height, tile_size):
        self._display = pygame.display.set_mode((width, height), pygame.RESIZABLE)
        self._tile_size = tile_size
        self._objects = []

    def refresh(self):
        for ele, position, type_ele in self._objects:
            if type_ele == 'tiled_map':
                ele.draw(self._display)
            elif type_ele == 'sprite':
                ele.blit(self._display, position)
            else:
                self._display.blit(ele, position)
        pygame.display.update()


    def AddSprite(self, sheet_file, pos_x = 0, pos_y = 0, rows=1, cols=1, begin = 0, end = -1):
        """The len is returned to know where is the sprite"""
        fullname = join('res', 'sprite', sheet_file)
        perso = pyganim.getImagesFromSpriteSheet(fullname,cols=cols,rows= rows)[begin:end]
        frames = list(zip(perso, [200, 200, 200, 200]))
        animObj = pyganim.PygAnimation(frames)
        animObj.play()
        self._objects.append([animObj, (pos_x, pos_y), 'sprite'])
        return len(self._objects)

    def AddMap(self, filename):
        fullname = join('res', 'map', filename)
        self._objects.append([TiledMap(fullname), (0, 0), 'tiled_map'])
        self._objects[-1][0].run()
        return len(self._objects)

    def AddTextBox(self, box, pos_x = 0, pos_y = 0):
        self._objects.append([box._box, (pos_x, pos_y), 'box'])
        self._objects.append([box._text,
                             (pos_x + box._text_pos_x, pos_y + box._text_pos_y),
                             'text'])
        return len(self._objects)-1, len(self._objects)

class TiledRenderer(object):
    """
    Super simple way to render a tiled map
    """

    def __init__(self, filename):
        tm = load_pygame(filename)

        # self.size will be the pixel size of the map
        # this value is used later to render the entire map to a pygame surface
        self.pixel_size = tm.width * tm.tilewidth, tm.height * tm.tileheight
        self.tmx_data = tm

    def render_map(self, surface):
        """ Render our map to a pygame surface
        The map MUST be of the same size as the surface
        There is no support for scrolling
        """

        # fill the background color of our render surface
        if self.tmx_data.background_color:
            surface.fill(pygame.Color(self.tmx_data.background_color))

        # iterate over all the visible layers, then draw them
        for layer in self.tmx_data.visible_layers:
            if isinstance(layer, TiledTileLayer):
                self.render_tile_layer(surface, layer)

            elif isinstance(layer, TiledObjectGroup):
                self.render_object_layer(surface, layer)

            elif isinstance(layer, TiledImageLayer):
                self.render_image_layer(surface, layer)

    def render_tile_layer(self, surface, layer):
        tw = self.tmx_data.tilewidth
        th = self.tmx_data.tileheight
        surface_blit = surface.blit
        for x, y, image in layer.tiles():
            surface_blit(image, (x * tw, y * th))

    def render_object_layer(self, surface, layer):
        draw_rect = pygame.draw.rect
        draw_lines = pygame.draw.lines
        surface_blit = surface.blit

        rect_color = (255, 0, 0)
        poly_color = (0, 255, 0)

        # iterate over all the objects in the layer
        for obj in layer:
            logger.info(obj)

            # objects with points are polygons or lines
            if hasattr(obj, 'points'):
                draw_lines(surface, poly_color, obj.closed, obj.points, 3)

            # some objects have an image
            # Tiled calls them "GID Objects"
            elif obj.image:
                surface_blit(obj.image, (obj.x, obj.y))

            # draw a rect for everything else
            # Mostly, I am lazy, but you could check if it is circle/oval
            # and use pygame to draw an oval here...I just do a rect.
            else:
                draw_rect(surface, rect_color,
                          (obj.x, obj.y, obj.width, obj.height), 3)

    def render_image_layer(self, surface, layer):
        if layer.image:
            surface.blit(layer.image, (0, 0))


class TiledMap(object):
    """ Basic app to display a rendered Tiled map
    """

    def __init__(self, filename):
        self.renderer = None
        self.load_map(filename)

    def load_map(self, filename):
        """ Create a renderer, load data
        """
        self.renderer = TiledRenderer(filename)

    def draw(self, surface):
        """ Draw our map to some surface (probably the display)
        """
        temp = pygame.Surface(self.renderer.pixel_size)
        self.renderer.render_map(temp)
        pygame.transform.smoothscale(temp, surface.get_size(), surface)

    def run(self):
        self.draw(screen._display)
        pygame.display.flip()

def CheckProperties(xy, P,  map_data):
    # Add a try, because if some properties aren't define on all tiles
    # there will be casualties
    try:
        x_id = xy[0]//tile_size
        y_id = xy[1]//tile_size
        gid = map_data.get_tile_gid(x_id, y_id,0)
        properties = map_data.get_tile_properties_by_gid(gid)
        print('CheckProperties', x_id, y_id, properties[P])
        return properties[P]
    except Exception as e:
        print('ERROR:',e)
        return 0

class TextBox():
    def __init__(self, box_file, text, height=0, width=0, pos_x = 0, pos_y = 0, size = 20):
        fullname = join('res', 'textbox', box_file)
        font = pygame.font.SysFont('freesans', size)
        self._text = font.render(text, True, (0,0,0))
        if height == 0 or width == 0:
            self._box =  pygame.image.load(fullname)
        else:
            img = pygame.image.load(fullname)
            self._box = pygame.transform.smoothscale(img, (width, height))
        self._text_pos_x = pos_x
        self._text_pos_y = pos_y

if __name__ == '__main__':
    tile_size = 29
    rows, cols = (144,12)
    begin, end = (0,4)
    pos_x, pos_y = (58,58)
    pygame.init()
    screen_height, screen_width = (640,640)
    screen = Screen(screen_height, screen_width, tile_size)

    map_index = screen.AddMap("sans-titre.tmx")
    sprite_index = screen.AddSprite("63468.png", rows = rows,  cols = cols,
                                    begin = begin, end = end,
                                    pos_x = pos_x, pos_y = pos_y)

    mainClock = pygame.time.Clock()
    map_data = screen._objects[map_index-1][0].renderer.tmx_data

    # We will make a object textbox to have the text and the box in the same place
    # It will be necessary to resize it
    string = 'Push enter to get the menu'
    box_file = "TextBox_LongSmall.png"
    text_box = TextBox(box_file, string, height=50, width=240, pos_x = 20, pos_y = 13)
    screen.AddTextBox(text_box)


    pygame.display.update()  # Initial display
    screen.refresh()

    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                rect = screen._objects[sprite_index-1][0].getRect()
                position_perso = screen._objects[sprite_index-1][1]
                temp_pos = position_perso
                if event.key == K_DOWN and position_perso[1] < screen_height-2*tile_size:
                    position_perso=rect.move(position_perso[0],position_perso[1] + tile_size)
                elif event.key == K_UP and position_perso[1] > 0:
                    position_perso=rect.move(position_perso[0],position_perso[1] - tile_size)
                elif event.key == K_LEFT and position_perso[0] > 0:
                    position_perso=rect.move(position_perso[0] - tile_size,position_perso[1])
                elif event.key == K_RIGHT and  position_perso[0] < screen_width-2*tile_size:
                    print( position_perso[0] < screen_width,position_perso[0],screen_width)
                    position_perso=rect.move(position_perso[0] + tile_size,position_perso[1])

                # Condition to be able to go to this tile
                p = CheckProperties(position_perso, 'slowness', map_data)
                if p == "-1":
                    position_perso = rect.move(temp_pos[0], temp_pos[1])
                screen._objects[sprite_index-1][1] = position_perso
                print("Anna's position:", position_perso[0],position_perso[1])
                print()
        screen.refresh()
        mainClock.tick(30)