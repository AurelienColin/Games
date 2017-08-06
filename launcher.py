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

# Text over any menu (not only !its! menu)
# Status minibox isn't updated whithout moving
# Remove hover when ECHAP aiming
# Remove hover on levelup
# Should do a void sprite sheet for Trade
# Should print items (and is equiped in the box status and items)
# Should print info about items (cara when use, equiped, unequiped, durability)