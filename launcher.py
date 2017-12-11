import py_functions.Screen as Screen
import py_functions.Loop as Loop

from os.path import join
import pygame


def Launcher():
    screenHeight, screenWidth = (870,870)
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
