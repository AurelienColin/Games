import py_functions.Screen as Screen
import py_functions.Loop as Loop

from os.path import join
import pygame

def Launcher():
    tileSize = 29
    pygame.init()
    global screenDim
    screenDim = (870,870)
    screen = Screen.Screen(screenDim[0], screenDim[1], tileSize)
    img = join('..', 'res', 'img', 'bg_main.png')
    background = pygame.image.load(img)
    screen.AddSprite(background, (0,0))

    while True:
        Loop.MenusLoop('LauncherMenu', screen)

if __name__ == '__main__':
    Launcher()