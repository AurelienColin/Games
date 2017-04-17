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
import pygame
from pygame.locals import *
from pytmx import *
from pytmx.util_pygame import load_pygame
import pytmx
import pyganim
import logging

logger = logging.getLogger(__name__)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
logger.addHandler(ch)
logger.setLevel(logging.INFO)


def init_screen(width, height):
    """ Set the screen mode
    This function is used to handle window resize events
    """
    return pygame.display.set_mode((width, height), pygame.RESIZABLE)

def AddSprite(sheet_file, rows, cols, begin = 0, end = -1):
    perso = pyganim.getImagesFromSpriteSheet(sheet_file,cols=cols,rows= rows)[begin:end]
    frames = list(zip(perso, [200, 200, 200, 200]))
    animObj = pyganim.PygAnimation(frames)
    animObj.play()
    return animObj


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
        Feel free to use this as a starting point for your pygame app.
        This method expects that the surface passed is the same pixel
        size as the map.

        Scrolling is a often requested feature, but pytmx is a map
        loader, not a renderer!  If you'd like to have a scrolling map
        renderer, please see my pyscroll project.
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
        # deref these heavily used references for speed
        tw = self.tmx_data.tilewidth
        th = self.tmx_data.tileheight
        surface_blit = surface.blit

        # iterate over the tiles in the layer
        for x, y, image in layer.tiles():
            surface_blit(image, (x * tw, y * th))

    def render_object_layer(self, surface, layer):
        # deref these heavily used references for speed
        draw_rect = pygame.draw.rect
        draw_lines = pygame.draw.lines
        surface_blit = surface.blit

        # these colors are used to draw vector shapes,
        # like polygon and box shapes
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


class SimpleTest(object):
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
        # first we make a temporary surface that will accommodate the entire
        # size of the map because this demo does not implement scrolling, we
        # render the entire map
        temp = pygame.Surface(self.renderer.pixel_size)
        # render the map onto the temporary surface
        self.renderer.render_map(temp)

        # now resize the temporary surface to the size of the display
        # this will also 'blit' the temp surface to the display
        pygame.transform.smoothscale(temp, surface.get_size(), surface)

    def run(self):
        self.draw(screen)
        pygame.display.flip()


if __name__ == '__main__':
    pygame.init()
    pygame.font.init()
    screen = init_screen(320, 320)
    pygame.display.set_caption('PyTMX Map Viewer')

    logger.info(pytmx.__version__)
    filename = "Res\\Map2.tmx"
    SimpleTest(filename).run()
    animObj = AddSprite("Res\\63468.png",  cols = 12, rows = 144, begin = 12, end = 16)

    mainClock = pygame.time.Clock()
    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
        screen.fill([0, 0, 0])
        SimpleTest(filename).run()
        animObj.blit(screen, (138, 138))
        pygame.display.update()
    mainClock.tick(30)