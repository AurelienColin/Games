from script import Screen, Loop
from os.path import join
import pygame

def Launcher():
    screen_height, screen_width = (640,640)
    tile_size = 29
    pygame.init()
    screen = Screen.Screen(screen_height, screen_width, tile_size)

    img = join('res', 'img', 'bg_main.png')
    background = pygame.image.load(img)
    screen.AddSprite(background, (0,0))

    while True:
        Loop.MenusLoop('LauncherMenu', screen)


if __name__ == '__main__':
    Launcher()