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
import util
import Team
from pygame.locals import *  # Import the event


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
        character.pos(tile_size, pos_pixel = new_pos)
    screen._objects[character._index[0]][1] = character._pos
    screen._objects[character._index[1]][1] = character._lifebar1._pos
    screen._objects[character._index[2]][1] = character._lifebar2._pos
    print("Character's position:", character._pos)
    return

def OpenMenu(key, screen, character=None, playerTeam=None):
    if key == 'MainMenu':
        text_box = TextBox.TextBox.Initialization('MainMenu')
    elif key == 'Skills':
        text_box = TextBox.TextBox.Initialization('Skills', character=character)
    pos_x = (screen_height - text_box._height)/2
    pos_y = (screen_width - text_box._width)/2
    menu_index = screen.AddTextBox(text_box, (pos_x, pos_y))

    alpha = 80
    color = (0,0,0)
    height, width, pos_x, pos_y = util.ObjToCoord(screen._objects[menu_index[1]])
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
        height, width, pos_x, pos_y = util.ObjToCoord(screen._objects[menu_index[selection]])
        s = Highlight.Highlight(width, height, alpha, color, pos_x, pos_y)
        selection_id = screen.AddHighlight(s)
    elif key == K_UP:
        screen.RemoveObject(selection_id)
        selection = (selection-1)%len(menu_index)
        if selection == 0:
            selection = len(menu_index)-1
        height, width, pos_x, pos_y = util.ObjToCoord(screen._objects[menu_index[selection]])
        s = Highlight.Highlight(width, height, alpha, color, pos_x, pos_y)
        selection_id = screen.AddHighlight(s)
    return selection, selection_id

def AimingLoop(current_character, screen, skill, map_data, playerTeam):
    blue = skill.Aim(current_character, screen, map_data, playerTeam)
    alpha = 80
    color = (255, 0, 0)
    red = {}
    selection_tile = current_character._pos_tile
    change = True
    while True:
        screen.refresh()
        mainClock.tick(30)
        for event in pygame.event.get():
            if event.type == QUIT:  # The game is closed
                pygame.quit()
                sys.exit()

            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:  # Return to skill menu
                    print('Return to skill menu')
                    for blue_id in blue.values():
                        screen.RemoveObject(blue_id)
                    for red_id in red.values():
                        screen.RemoveObject(red_id)
                    return False  # We didn't used the skill
                elif event.key == K_RETURN:  # We use the skill
                    util.Attack(current_character, skill, red, playerTeam, map_data)
                elif event.key == K_KP2 or event.key == K_DOWN:
                    if (selection_tile[0], selection_tile[1]+1) in blue:
                        selection_tile = (selection_tile[0], selection_tile[1]+1)
                        change = True
                elif event.key == K_KP8 or event.key == K_UP:
                    if (selection_tile[0], selection_tile[1]-1) in blue:
                        selection_tile = (selection_tile[0], selection_tile[1]-1)
                        change = True
                elif event.key == K_KP4 or event.key == K_LEFT:
                    if (selection_tile[0]-1, selection_tile[1]) in blue:
                        selection_tile = (selection_tile[0]-1, selection_tile[1])
                        change = True
                elif event.key == K_KP6 or event.key == K_RIGHT:
                    if (selection_tile[0]+1, selection_tile[1]) in blue:
                        selection_tile = (selection_tile[0]+1, selection_tile[1])
                        change = True
                elif event.key == K_KP7:
                    if (selection_tile[0]-1, selection_tile[1]-1) in blue:
                        selection_tile = (selection_tile[0]-1, selection_tile[1]-1)
                        change = True
                elif event.key == K_KP9:
                    if (selection_tile[0]+1, selection_tile[1]-1) in blue:
                        selection_tile = (selection_tile[0]+1, selection_tile[1]-1)
                        change = True
                elif event.key == K_KP3:
                    if (selection_tile[0]+1, selection_tile[1]+1) in blue:
                        selection_tile = (selection_tile[0]+1, selection_tile[1]+1)
                        change = True
                elif event.key == K_KP1:
                    if (selection_tile[0]-1, selection_tile[1]+1) in blue:
                        selection_tile = (selection_tile[0]-1, selection_tile[1]+1)
                        change = True
            if change:
                change = False
                selection_tiles = skill.AOE(selection_tile, current_character, screen)
                s = Highlight.HighlightTiles(screen._tile_size, selection_tiles, alpha, color)
                for red_id in red.values():
                    screen.RemoveObject(red_id)
                red = {}
                for pos in s:
                        red[pos] = screen.AddHighlight(s[pos])


def MenusLoop(menu, current_character, screen, map_data, playerTeam):
    menus = [menu]
    selection = 1
    menu_index, selection_id = OpenMenu('MainMenu', screen)
    choice = None
    while True:
        screen.refresh()
        mainClock.tick(30)
        for event in pygame.event.get():
            if event.type == QUIT:  # The game is closed
                pygame.quit()
                sys.exit()

            if event.type == KEYDOWN:
                ####### We are doing something in the menu ######
                if event.key == K_RETURN:  # We open a menu
                    choice = screen._objects[menu_index[0]][0]._string[selection-1]
                    if choice in skills: # We use a skill
                        for skill in current_character._skills:
                            if choice == skill._name:
                                print('Aim with skill', choice)
                                QuitMenu(screen, menu_index, selection_id)
                                selection = 1
                                use = AimingLoop(current_character, screen, skill, map_data, playerTeam)
                                if not use:
                                    menu_index, selection_id = OpenMenu(menus[-1], screen, character=current_character)
                                else:
                                    return

                    elif choice in implemented_menu:
                        print('Open menu:', choice)
                        menus.append(choice)
                        old_menu_index, old_selection_id = menu_index, selection_id
                        menu_index, selection_id = OpenMenu(menus[-1], screen, character=current_character)
                        QuitMenu(screen, old_menu_index, old_selection_id)
                        selection = 1
                    else: # Nothing
                        pass
                if event.key == K_UP or event.key == K_DOWN:  # We navigate through the menu
                    selection, selection_id = MenuNavigation(event.key, screen, menu_index, selection, selection_id)

                ##### We are closing a menu #####
                if event.key == K_ESCAPE or choice == 'Exit':
                    if len(menus) > 1:  # Go to the previous menu
                        menus.pop(-1)
                        print('Return to menu:', menus[-1])
                        QuitMenu(screen, menu_index, selection_id)
                        menu_index, selection_id = OpenMenu(menus[-1], screen, character=current_character)
                        selection = 1
                    else: # We quit the last menu
                        menus = []
                        QuitMenu(screen, menu_index, selection_id)
                        return

def MovementLoop(current_character, screen, map_data):
    while True:
        screen.refresh()
        mainClock.tick(30)
        for event in pygame.event.get():
            if event.type == QUIT:  # The game is closed
                pygame.quit()
                sys.exit()

            if event.type == KEYDOWN:
                if event.key == K_RETURN:
                    print('Opening main menu')
                    return 'MainMenu'
                if event.key == K_UP or event.key == K_DOWN or event.key == K_RIGHT or event.key == K_LEFT:
                    # We move the current character
                    IfDeplacement(current_character, event.key, screen, map_data)


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
    anna.pos(tile_size, pos_tile = (2, 2))
    anna.AddLifeBar(tile_size)
    anna._index = screen.AddCharacter(anna, 'standing')
    playerTeam = Team.Team(1, [anna], tile_size)

    henry = Character.Character.Initialization('Henry')
    henry.pos(tile_size, pos_tile = (10, 4))
    henry.AddLifeBar(tile_size)
    henry._index = screen.AddCharacter(henry, 'standing')
    opponentTeam = Team.Team(2, [henry], tile_size)

    teams = [playerTeam, opponentTeam]
    playerTeam._team_opponent.append(opponentTeam._number)
    opponentTeam._team_opponent.append(playerTeam._number)
    playerTeam.relations(teams)
    opponentTeam.relations(teams)

    string = 'Push enter to get the menu'
    box_file = "TextBox_LongSmall.png"
    text_box = TextBox.TextBox(box_file, string, 50, 240, (20, 13))
    screen.AddTextBox(text_box, (100,0))

    mainClock = pygame.time.Clock()
    pygame.display.update()  # Initial display
    screen.refresh()

    current_character = anna
    skills = Skill.ListSkills()
    implemented_menu = TextBox.ListMenus()

    while True:
        menu = MovementLoop(current_character, screen, map_data)
        MenusLoop(menu, current_character, screen, map_data, playerTeam)