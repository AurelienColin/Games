from script import Screen, Level
import pygame

if __name__ == '__main__':
    screen_height, screen_width = (640,640)
    tile_size = 29
    pygame.init()
    screen = Screen.Screen(screen_height, screen_width, tile_size)
    level = Level.Level(screen, 'level0')