import sys

import pygame
from pygame.locals import K_SPACE, K_RETURN, QUIT, K_UP, K_DOWN, K_LEFT, K_RIGHT


def manual_input():
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    keys = pygame.key.get_pressed()
    actions = [keys[K_UP], keys[K_DOWN], keys[K_RIGHT], keys[K_LEFT], keys[K_SPACE]]

    return actions


