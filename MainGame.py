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

if __name__ == '__main__':
    tile_size = 29
    rows, cols = (144,12)
    begin, end = (0,4)
    pos_x, pos_y = (58,58)
    pygame.init()
    screen_height, screen_width = (640,640)
    screen = Screen.Screen(screen_height, screen_width, tile_size)

    map_index = screen.AddMap("sans-titre.tmx")
    sprite_index = screen.AddSprite("63468.png", rows = rows,  cols = cols,
                                    begin = begin, end = end,
                                    pos_x = pos_x, pos_y = pos_y)

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
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if not selection:
                    rect = screen._objects[sprite_index][0].getRect()
                    position_perso = screen._objects[sprite_index][1]
                    temp_pos = position_perso
                    if event.key == K_DOWN and position_perso[1] < screen_height-2*tile_size:
                        position_perso=rect.move(position_perso[0],position_perso[1] + tile_size)
                    elif event.key == K_UP and position_perso[1] > 0:
                        position_perso=rect.move(position_perso[0],position_perso[1] - tile_size)
                    elif event.key == K_LEFT and position_perso[0] > 0:
                        position_perso=rect.move(position_perso[0] - tile_size,position_perso[1])
                    elif event.key == K_RIGHT and  position_perso[0] < screen_width-2*tile_size:
                        position_perso=rect.move(position_perso[0] + tile_size,position_perso[1])
                    screen._objects[sprite_index][1] = position_perso

                if event.key == K_RETURN and not menu:
                    string = 'Aide\nSkills\nObjets\nStatus\nExit'
                    height, width = (150, 100)
                    text_box = TextBox.TextBox("TextBox_ExtraLarge.png", string,
                                               height = height, width = width,
                                               pos_x = 30, pos_y = 20)
                    pos_x = (screen_height - height)/2
                    pos_y = (screen_width - width)/2
                    menu_index = screen.AddTextBox(text_box, pos_x, pos_y)
                    menu = True

                    selection = 1
                    print(menu_index[selection], screen._objects[menu_index[selection]])
                    height, width, pos_x, pos_y = ObjToCoord(screen._objects[menu_index[selection]])

                    # We should take the width of the textbox for highligh

                    selection_id = screen.AddHighlight(height, width, 128, (0,0,0), pos_x, pos_y)
                if event.key == K_ESCAPE and menu:
                    for i in menu_index:
                        screen.RemoveObject(i)
                        menu = False
                if selection and event.key == K_DOWN:
                    screen.RemoveObject(selection_id)
                    selection = (selection+1)%len(menu_index)
                    if selection == 0:
                        selection +=1
                    height, width, pos_x, pos_y = ObjToCoord(screen._objects[menu_index[selection]])
                    selection_id = screen.AddHighlight(height, width, 128, (0,0,0), pos_x, pos_y)
                if selection and event.key == K_UP:
                    screen.RemoveObject(selection_id)
                    selection = (selection-1)%len(menu_index)
                    if selection == 0:
                        selection +=1
                    height, width, pos_x, pos_y = ObjToCoord(screen._objects[menu_index[selection]])
                    selection_id = screen.AddHighlight(height, width, 128, (0,0,0), pos_x, pos_y)


                # Condition to be able to go to this tile
                p = Map.CheckProperties(position_perso, 'slowness', map_data, tile_size)
                if p == "-1":
                    position_perso = rect.move(temp_pos[0], temp_pos[1])

                print("Anna's position:", position_perso[0],position_perso[1])
                print()
        screen.refresh()
        mainClock.tick(30)