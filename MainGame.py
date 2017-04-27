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
import Class
import Skill
import Screen
import Map
import TextBox
from pygame.locals import *

def ObjToCoord(obj):
    rect = obj[0].get_rect()
    pos_x, pos_y = obj[1]
    print('coord:',rect.height, rect.width, pos_x, pos_y)
    return rect.height, rect.width, pos_x, pos_y

def IfDeplacement(personnage_index, key, screen, map_data):
    rect = screen._objects[personnage_index][0].getRect()
    position = screen._objects[personnage_index][1]
    temp_pos = position
    tile_size = screen._tile_size
    if key == K_DOWN and position[1] < screen_height-2*tile_size:
        position=rect.move(position[0], position[1] + tile_size)
    elif key == K_UP and position[1] > 0:
        position=rect.move(position[0], position[1] - tile_size)
    elif key == K_LEFT and position[0] > 0:
        position=rect.move(position[0] - tile_size, position[1])
    elif key == K_RIGHT and position[0] < screen_width-2*tile_size:
        position=rect.move(position[0] + tile_size, position[1])
    # Condition to be able to go to this tile
    p = Map.CheckProperties(position, 'slowness', map_data, tile_size)
    if p == "-1":
        position = rect.move(temp_pos[0], temp_pos[1])
    screen._objects[personnage_index][1] = position
    print("Character's position:", int(position[0]/tile_size), int(position[1]/tile_size))
    return position

def OpenMenu(screen):
    string = 'Aide\nSkills\nObjets\nStatus\nExit'
    height, width = (150, 100)
    text_box = TextBox.TextBox("TextBox_ExtraLarge.png", string, height = height,
                               width = width, pos_x = 30, pos_y = 20)

    pos_x = (screen_height - height)/2
    pos_y = (screen_width - width)/2
    menu_index = screen.AddTextBox(text_box, pos_x, pos_y)

    alpha = 80
    color = (0,0,0)
    height, width, pos_x, pos_y = ObjToCoord(screen._objects[menu_index[selection]])
    selection_id = screen.AddHighlight(width,height, alpha, color, pos_x, pos_y)
    return menu_index, selection_id

def MenuNavigation(key, screen, menu_index, selection, selection_id):
    alpha = 80
    color = (0,0,0)
    if key == K_DOWN:
        screen.RemoveObject(selection_id)
        selection = (selection+1)%len(menu_index)
        if selection == 0:
            selection +=1
        height, width, pos_x, pos_y = ObjToCoord(screen._objects[menu_index[selection]])
        selection_id = screen.AddHighlight( width,height, alpha, color, pos_x, pos_y)
    elif key == K_UP:
        screen.RemoveObject(selection_id)
        selection = (selection-1)%len(menu_index)
        if selection == 0:
            selection = len(menu_index)-1
        height, width, pos_x, pos_y = ObjToCoord(screen._objects[menu_index[selection]])
        selection_id = screen.AddHighlight(width,height, alpha, color, pos_x, pos_y)
    return selection, selection_id

def QuitMenu(screen, menu_index, selection_id):
    for i in menu_index:
        screen.RemoveObject(i)
    screen.RemoveObject(selection_id)

if __name__ == '__main__':
    tile_size = 29
    pygame.init()
    screen_height, screen_width = (640,640)
    screen = Screen.Screen(screen_height, screen_width, tile_size)

    map_index = screen.AddMap("sans-titre.tmx")
    anna_index = screen.AddSprite("63468.png", rows = 144,  cols = 12,
                                    begin = 0, end = 4,
                                    pos_x = 2*tile_size, pos_y = 2*tile_size)
    henry_index = screen.AddSprite("63482.png", rows = 80,  cols = 12,
                                    begin = 384, end = 388,
                                    pos_x = 10*tile_size, pos_y = 4*tile_size)

    mainClock = pygame.time.Clock()
    map_data = screen._objects[map_index][0].renderer.tmx_data

    string = 'Push enter to get the menu'
    box_file = "TextBox_LongSmall.png"
    text_box = TextBox.TextBox(box_file, string, height=50, width=240,
                               pos_x = 20, pos_y = 13)
    screen.AddTextBox(text_box, pos_x = 100)


    pygame.display.update()  # Initial display
    screen.refresh()
    menu = False
    selection = 0
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:  # The game is closed
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if menu:  # We are in a menu
                    if event.key == K_ESCAPE: # We close the menu
                        menu = False
                        selection = 0
                        QuitMenu(screen, menu_index, selection_id)
                    elif event.key == K_UP or event.key == K_DOWN:  # We navigate through the menu
                        selection, selection_id = MenuNavigation(event.key, screen, menu_index, selection, selection_id)
                    elif event.key == K_RETURN: # We selection the menu item
                        pass # Not yet implemented
                else:  # We are on the map
                    if event.key == K_RETURN: # We open a menu
                        menu = True
                        selection = 1
                        menu_index, selection_id = OpenMenu(screen)
                    elif event.key == K_UP or event.key == K_DOWN or event.key == K_RIGHT or event.key == K_LEFT:
                        # We move the current character
                        anna_position = IfDeplacement(anna_index, event.key, screen, map_data)
                print()
        screen.refresh()
        mainClock.tick(30)