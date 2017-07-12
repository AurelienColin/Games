from py import Screen, Loop
from os.path import join
import pygame


def Launcher():
    screenHeight, screenWidth = (640,640)
    tileSize = 29
    pygame.init()

    screen = Screen.Screen(screenHeight, screenWidth, tileSize)
    img = join('res', 'img', 'bg_main.png')
    background = pygame.image.load(img)
    screen.AddSprite(background, (0,0))

    while True:
        Loop.MenusLoop('LauncherMenu', screen)

if __name__ == '__main__':
    Launcher()


# Status minibox (in the bottom right corner) isn't updating