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
import Character
import Screen
import Map
import TextBox
import Skill
import Highlight
from pygame.locals import *  # Import the event

def ObjToCoord(obj):
    rect = obj[0].get_rect()
    pos_x, pos_y = obj[1]
    return rect.height, rect.width, pos_x, pos_y

def IfDeplacement(character, key, screen, map_data):
    position = character._pos
    tile_size = screen._tile_size
    if key == K_DOWN and position[1] < screen_height-2*tile_size:
        diff = (0, tile_size)
    elif key == K_UP and position[1] > 0:
        diff = (0, -tile_size)
    elif key == K_LEFT and position[0] > 0:
        diff = (-tile_size, 0)
    elif key == K_RIGHT and position[0] < screen_width-2*tile_size:
        diff = (tile_size, 0)
    else:
        diff = (0, 0)
    new_pos = (position[0]+diff[0] , position[1]+diff[1])
    change = True
    for obj in screen._objects:
        if obj and obj[2] == 'character' and obj != screen._objects[character._index[1]] and obj[1] == new_pos:
            change = False
    p = Map.CheckProperties(new_pos, 'slowness', map_data, tile_size)
    if p == "-1":
        change = False
    if change:
        character._lifebar1._pos = (character._lifebar1._pos[0] + diff[0], character._lifebar1._pos[1] + diff[1])
        character._lifebar2._pos = (character._lifebar2._pos[0] + diff[0], character._lifebar2._pos[1] + diff[1])
        character._pos = new_pos
    screen._objects[character._index[0]][1] = character._pos
    screen._objects[character._index[1]][1] = character._lifebar1._pos
    screen._objects[character._index[2]][1] = character._lifebar2._pos
    print("Character's position:", int(position[0]/tile_size), int(position[1]/tile_size))
    return position

def OpenMenu(key, screen, character=None, team=None):
    if key == 'MainMenu':
        text_box = TextBox.TextBox.Initialization('MainMenu')
    elif key == 'Skills':
        text_box = TextBox.TextBox.Initialization('Skills', character=character)
    pos_x = (screen_height - text_box._height)/2
    pos_y = (screen_width - text_box._width)/2
    menu_index = screen.AddTextBox(text_box, (pos_x, pos_y))

    alpha = 80
    color = (0,0,0)
    height, width, pos_x, pos_y = ObjToCoord(screen._objects[menu_index[1]])
    s = Highlight.Highlight(width, height, alpha, color, pos_x, pos_y)
    selection_id = screen.AddHighlight(s)
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
        s = Highlight.Highlight(width, height, alpha, color, pos_x, pos_y)
        selection_id = screen.AddHighlight(s)
    elif key == K_UP:
        screen.RemoveObject(selection_id)
        selection = (selection-1)%len(menu_index)
        if selection == 0:
            selection = len(menu_index)-1
        height, width, pos_x, pos_y = ObjToCoord(screen._objects[menu_index[selection]])
        s = Highlight.Highlight(width, height, alpha, color, pos_x, pos_y)
        selection_id = screen.AddHighlight(s)
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

    map_index = screen.AddMap("TestLevel.tmx")
    map_data = screen._objects[map_index][0].renderer.tmx_data

    anna = Character.Character.Initialization('Anna')
    anna._pos = (2*tile_size, 2*tile_size)
    anna.AddLifeBar(tile_size)
    anna._index = screen.AddCharacter(anna, 'standing')

    henry = Character.Character.Initialization('Henry')
    henry._pos = (10*tile_size, 4*tile_size)
    henry.AddLifeBar(tile_size)
    henry._index = screen.AddCharacter(henry, 'standing')


    string = 'Push enter to get the menu'
    box_file = "TextBox_LongSmall.png"
    text_box = TextBox.TextBox(box_file, string, 50, 240, (20, 13))
    screen.AddTextBox(text_box, (100,0))


    mainClock = pygame.time.Clock()
    pygame.display.update()  # Initial display
    screen.refresh()
    selection = 0
    menus = []
    current_character = anna
    skills = Skill.ListSkills()
    implemented_menu = TextBox.ListMenus()
    choice = None
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:  # The game is closed
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if menus:  # We are in a menu
                    if event.key == K_RETURN:
                        choice = screen._objects[menu_index[0]][0]._string[selection-1]
                        if choice not in skills and choice != 'Exit' and choice in implemented_menu:
                            menus.append(choice)
                            old_menu_index, old_selection_id = menu_index, selection_id
                            menu_index, selection_id = OpenMenu(menus[-1], screen, character=current_character)
                            QuitMenu(screen, old_menu_index, old_selection_id)
                            selection = 1
                        else: # We selection a skill
                            pass

                    if event.key == K_ESCAPE or choice == 'Exit': # We close the menu
                        choice = None
                        if len(menus) > 1:  # Go to the previous menu
                            menus.pop(-1)
                            print('Go to', menus[-1])
                            QuitMenu(screen, menu_index, selection_id)
                            menu_index, selection_id = OpenMenu(menus[-1], screen, character=current_character)
                            selection = 1
                        elif len(menus) == 1: # We quit the last menu
                            menus = []
                            QuitMenu(screen, menu_index, selection_id)
                            selection = 0
                    elif event.key == K_UP or event.key == K_DOWN:  # We navigate through the menu
                        selection, selection_id = MenuNavigation(event.key, screen, menu_index, selection, selection_id)

                else:  # We are on the map
                    if event.key == K_RETURN: # We open a menu
                        menus.append('MainMenu')
                        selection = 1
                        menu_index, selection_id = OpenMenu('MainMenu', screen)
                    elif event.key == K_UP or event.key == K_DOWN or event.key == K_RIGHT or event.key == K_LEFT:
                        # We move the current character
                        anna_position = IfDeplacement(current_character, event.key, screen, map_data)
        screen.refresh()
        mainClock.tick(30)