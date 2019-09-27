import pygame
import os
from functools import lru_cache

from pygame.transform import rotate
from pygame.mask import from_surface

from Rignak_Misc.path import get_local_file

SPRITE_ROOT = get_local_file(__file__, os.path.join('sprites'))
SCALING_FACTOR = 0.5

def set_scaling_factor(scaling_factor):
    global SCALING_FACTOR
    SCALING_FACTOR = scaling_factor

@lru_cache(maxsize=128)
def load_sprite(filename, sprite_root=SPRITE_ROOT, scaling_factor=SCALING_FACTOR):
    sprite = pygame.image.load(os.path.join(sprite_root, filename))
    height, width = sprite.get_rect().size
    sprite = pygame.transform.scale(sprite, (int(height * scaling_factor), int(width * scaling_factor)))
    return sprite



class Sprite:
    def __init__(self, sprite_filename, x, y, angle, sprite_root=SPRITE_ROOT):
        self.x = x
        self.y = y
        self.angle = angle
        self.original_sprite = load_sprite(sprite_filename, sprite_root=sprite_root)
        self.original_size = self.original_sprite.get_rect().size
        self.x -= self.original_size[0] // 2
        self.y -= self.original_size[1] // 2
        self.current_sprite = load_sprite(sprite_filename, sprite_root=sprite_root)
        self.rect = self.current_sprite.get_rect()
        self.move(self.x, self.y, self.angle)

    def rotate(self, angle):
        self.angle = angle
        self.current_sprite = rotate(self.original_sprite, self.angle)
        self.mask = from_surface(self.current_sprite)
        self.rect = self.current_sprite.get_rect()

    def move(self, x, y, angle):
        self.rotate(angle)
        self.current_size = self.rect.size

        self.rect.center = (x + self.original_size[0] // 2,
                            y + self.original_size[1] // 2)  # TODO*
