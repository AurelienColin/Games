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
import Level
import Effect
from pygame.locals import *  # Import the event

def IfDeplacement(character, key, screen):
    position = character._pos_tile
    tile_size = screen._tile_size
    if key == K_DOWN and position[1] < screen._height//tile_size:
        new_pos = (position[0], position[1]+1)
    elif key == K_UP and position[1] > 0:
        new_pos = (position[0], position[1]-1)
    elif key == K_LEFT and position[0] > 0:
        new_pos = (position[0]-1, position[1])
    elif key == K_RIGHT and position[0] < screen._width//tile_size:
        new_pos = (position[0]+1, position[1])
    else:
        new_pos = position
    print('Move from', position, 'to', new_pos)
    px_pos = new_pos[0]*screen._tile_size, new_pos[1]*screen._tile_size
    change = True
    for other_char in screen._characters:
        if not other_char._dead and other_char._pos == px_pos and character != other_char:
            change = False
    p = int(Map.CheckProperties(px_pos, 'slowness', screen._map_data, tile_size))
    if p == -1 or p > character._cara['PM']:
        change = False
    if change:
        character.Move(screen, p, character._pos_tile, new_pos)
    return

def AimingLoop(current_character, screen, skill):
    blue = skill.Aim(current_character, screen)
    alpha = 80
    color = (255, 0, 0)
    red = {}
    selection_tile = current_character._pos_tile
    change = True
    end = False
    mainClock = pygame.time.Clock()
    skillDetails = screen.AddTextBox(TextBox.SkillDetails(skill),
                                     (screen._height-128,screen._width-2*100))
    while True:
        screen.refresh()
        mainClock.tick(30)
        for event in pygame.event.get():
            if event.type == QUIT:  # The game is closed
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN:
                if event.key == K_RETURN and current_character._cara['PA'] > skill._cost:  # We use the skill
                    current_character.Attack(skill, red, screen, selection_tile)
                    end = True
                    screen.UpdateStatus(current_character)
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

            elif event.type == MOUSEMOTION:
                screen.onHover(event.pos)

            if (event.type == KEYDOWN and event.key == K_ESCAPE) or end:# Return to skill menu
                print('Return to skill menu')
                to_remove = list(blue.values()) + list(red.values()) + skillDetails
                for index in to_remove:
                    screen.RemoveObject(index)
                if end:
                    return True
                return False

            if change:
                change = False
                selection_tiles = skill.AOE(selection_tile, current_character, screen)
                s = Highlight.HighlightTiles(screen._tile_size, selection_tiles, alpha, color)
                for red_id in red.values():
                    screen.RemoveObject(red_id)
                red = {}
                for pos in s:
                        red[pos] = screen.AddHighlight(s[pos])

def MenusLoop(menu, current_character, screen):
    skills = Skill.ListSkills()
    implemented_menu = TextBox.ListMenus()
    menus = [menu]
    selection = 1
    menu_index, selection_id = screen.OpenMenu('MainMenu')
    choice = None
    mainClock = pygame.time.Clock()
    while True:
        screen.refresh()
        mainClock.tick(30)
        for event in pygame.event.get():
            if event.type == QUIT:  # The game is closed
                pygame.quit()
                sys.exit()

            elif event.type == KEYDOWN:
                ####### We are doing something in the menu ######
                if event.key == K_RETURN:  # We open a menu
                    choice = screen._objects[menu_index[0]][0]._string[selection-1]
                    if choice in skills: # We use a skill
                        for skill in current_character._skills:
                            if choice == skill._name:
                                print('Aim with skill', choice)
                                screen.QuitMenu(menu_index, selection_id)
                                selection = 1
                                use = AimingLoop(current_character, screen, skill)
                                if not use:
                                    menu_index, selection_id = screen.OpenMenu(menus[-1], character=current_character)
                                else:
                                    return

                    elif choice in implemented_menu:
                        print('Open menu:', choice)
                        menus.append(choice)
                        old_menu_index, old_selection_id = menu_index, selection_id
                        menu_index, selection_id = screen.OpenMenu(menus[-1], character=current_character)
                        screen.QuitMenu(old_menu_index, old_selection_id)
                        selection = 1
                    else: # Nothing
                        pass
                if event.key == K_UP or event.key == K_DOWN:  # We navigate through the menu
                    selection, selection_id = screen.MenuNavigation(event.key, menu_index, selection, selection_id)
                if screen._status_box != -1 and (event.key == K_RIGHT or event.key == K_LEFT):
                    screen.QuitMenu(menu_index, selection_id)
                    if event.key == K_RIGHT:
                        j = -1
                    else:
                        j = 1
                    screen._status_box = (screen._status_box+j)%len(screen._characters)
                    menu_index, selection_id = screen.OpenMenu('Status')
                    screen.RemoveObject(selection_id)
                ##### We are closing a menu #####
                if event.key == K_ESCAPE or choice == 'Exit' or choice == 'End Turn':
                    if screen._childBox:
                        for index in screen._childBox:
                            screen.RemoveObject(index)
                        screen._childBox = False
                    if len(menus) > 1:  # Go to the previous menu
                        menus.pop(-1)
                        print('Return to menu:', menus[-1])
                        screen.QuitMenu(menu_index, selection_id)
                        menu_index, selection_id = screen.OpenMenu(menus[-1], character=current_character)
                        selection = 1
                        screen._status_box = -1
                    else: # We quit the last menu
                        menus = []
                        screen.QuitMenu(menu_index, selection_id)
                        return choice

def MovementLoop(current_character, screen):
    mainClock = pygame.time.Clock()
    while True:
        screen.refresh()
        mainClock.tick(30)
        for event in pygame.event.get():
            if event.type == QUIT:  # The game is closed
                pygame.quit()
                sys.exit()

            elif event.type == KEYDOWN:
                if event.key == K_RETURN:
                    print('Opening main menu')
                    return 'MainMenu'
                if event.key == K_UP or event.key == K_DOWN or event.key == K_RIGHT or event.key == K_LEFT:
                    # We move the current character
                    IfDeplacement(current_character, event.key, screen)

            elif event.type == MOUSEMOTION:
                screen.onHover(event.pos)

def PlacementLoop(ini_tiles, screen):
    highlighted = Highlight.HighlightTiles(screen._tile_size, ini_tiles,60, (0, 0,255))
    blue, red = {}, [False, False]
    for pos in highlighted:
        blue[pos] = screen.AddHighlight(highlighted[pos])
    l = list(blue.keys())
    selection = 0
    s = Highlight.HighlightTiles(screen._tile_size,l[selection], 120, (255, 0, 0))
    red = [screen.AddHighlight(s[l[selection]]), l[selection]]

    mainClock = pygame.time.Clock()
    while True:
        screen.refresh()
        mainClock.tick(30)
        change = False
        for event in pygame.event.get():
            if event.type == QUIT:  # The game is closed
                pygame.quit()
                sys.exit()

            elif event.type == KEYDOWN:
                if event.key == K_RIGHT:
                    selection = (selection+1)%len(l)
                    change = True
                elif event.key == K_LEFT:
                    selection = (selection-1)%len(l)
                    change = True
                elif event.key == K_RETURN:
                    menu_index, selection_id = screen.OpenMenu('Status')

            if change:
                screen.RemoveObject(red[0])
                s = Highlight.HighlightTiles(screen._tile_size,l[selection],
                                             120, (255, 0, 0))
                red = [screen.AddHighlight(s[l[selection]]), l[selection]]


if __name__ == '__main__':
    screen_height, screen_width = (640,640)
    tile_size = 29
    pygame.init()
    screen = Screen.Screen(screen_height, screen_width, tile_size)
    level = Level.Level_0(screen)
    level.ModeTRPG()