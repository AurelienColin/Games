"""
"""
import sys
import pygame
from . import Map, TextBox, Skill, Highlight, util
from os.path import join
from pygame.locals import *  # Import the event

def IfDeplacement(character, key, screen):
    """Move a character on the screen, after checking if the move is allowed

    Input:
    character - character
    key - K_DOWN, K_UP, K_LEFT or K_RIGHT
    screen - screen
    """
    position = character._tile
    tile_size = screen._tile_size
    if key == K_DOWN and position[1] < screen._size[0]//tile_size:
        new_pos = (position[0], position[1]+1)
    elif key == K_UP and position[1] > 0:
        new_pos = (position[0], position[1]-1)
    elif key == K_LEFT and position[0] > 0:
        new_pos = (position[0]-1, position[1])
    elif key == K_RIGHT and position[0] < screen._size[1]//tile_size:
        new_pos = (position[0]+1, position[1])
    else:
        new_pos = position
    print('Move from', position, 'to', new_pos)
    px_pos = new_pos[0]*screen._tile_size, new_pos[1]*screen._tile_size
    change = True
    for other_char in screen._characters:
        if not other_char._dead and other_char._pixel == px_pos and character != other_char:
            change = False
    p = int(Map.CheckProperties(px_pos, 'slowness', screen._map_data, tile_size))
    if p == -1 or p > character._cara['PM']:
        change = False
    if change:
        character.Move(screen, p, character._tile, new_pos)
    return

def AimingLoop(current_character, screen, skill):
    """Action Loop: current_character choose a target for it's skill or return
    current_character - character
    screen - screen
    skill - skill

    Output
    boolean - True if a skill is used, else False"""
    blue = skill.Aim(current_character, screen)
    alpha = 80
    color = (255, 0, 0)
    red = {}
    tile = current_character._tile
    change = True
    end = False
    mainClock = pygame.time.Clock()
    skillDetails = screen.AddTextBox(TextBox.SkillDetails(skill, current_character),
                                     (screen._size[0]-128,screen._size[1]-2*100))
    while True:
        screen.refresh()
        mainClock.tick(30)
        for event in pygame.event.get():
            if event.type == QUIT:  # The game is closed
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN:
                change = True
                if event.key == K_RETURN and current_character._cara['PA'] > skill._cara['cost']:
                    current_character.Attack(skill, red, screen, tile)
                    end = True
                    screen.UpdateStatus(current_character)
                    for i in screen._ui['hovering']:
                        screen.RemoveObject(i)
                    screen._ui['hovering'] = []
                elif event.key == K_DOWN and (tile[0], tile[1]+1) in blue:
                        tile = (tile[0], tile[1]+1)
                elif event.key == K_UP and (tile[0], tile[1]-1) in blue:
                        tile = (tile[0], tile[1]-1)
                elif event.key == K_LEFT and (tile[0]-1, tile[1]) in blue:
                        tile = (tile[0]-1, tile[1])
                elif event.key == K_RIGHT and  (tile[0]+1, tile[1]) in blue:
                    tile = (tile[0]+1, tile[1])
            elif event.type == MOUSEMOTION:
                mouse_pos = screen.onHover(event.pos)
                if mouse_pos in blue:
                    change = True
                    tile = mouse_pos

            if (event.type == KEYDOWN and event.key == K_ESCAPE) or end:# Return to skill menu
                print('Return to skill menu')
                for index in list(blue.values()) + list(red.values()) + skillDetails:
                    screen.RemoveObject(index)
                if end:
                    return True
                return False

            if change:
                change = False
                tiles = skill.AOE(tile, current_character, screen)
                s = Highlight.HighlightTiles(screen._tile_size, tiles, alpha, color)
                for index in list(red.values()):
                    screen.RemoveObject(index)
                red = {}
                for pos in s:
                        red[pos] = screen.AddHighlight(s[pos])
                screen.onHover((tile[0]*screen._tile_size, tile[1]*screen._tile_size))

def MenusLoop(menu, screen, current_character=None):
    """Action Loop: current_character navigate in the menus
    menu - string: name of the menu entered
    current_character - character
    screen - screen

    Output
    None if a skill is used
    'Exit' or 'End Turn': reason to quit the menus"""
    skills = Skill.ListSkills()
    implemented_menu = TextBox.ListMenus()
    menus = [menu]
    selection = 1
    menu_index, selection_id = screen.OpenMenu(menu)
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
                    if current_character and choice in skills: # We use a skill
                        for skill in current_character._skills:
                            if choice == skill._cara['name']:
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
                if screen._charBox != -1 and (event.key == K_RIGHT or event.key == K_LEFT):
                    screen.QuitMenu(menu_index, selection_id)
                    if event.key == K_RIGHT:
                        j = -1
                    else:
                        j = 1
                    screen._charBox = (screen._charBox+j)%len(screen._characters)
                    menu_index, selection_id = screen.OpenMenu('Status')
                    screen.RemoveObject(selection_id)
                ##### We are closing a menu #####
                if event.key == K_ESCAPE or choice == 'Exit' or choice == 'End Turn':
                    for index in screen._ui['childBox'] + screen._ui['hovering']:
                        screen.RemoveObject(index)
                    screen._ui['childBox'] = []
                    screen._ui['hovering'] = []
                    if len(menus) > 1:  # Go to the previous menu
                        menus.pop(-1)
                        print('Return to menu:', menus[-1])
                        screen.QuitMenu(menu_index, selection_id)
                        menu_index, selection_id = screen.OpenMenu(menus[-1], character=current_character)
                        selection = 1
                        screen._charBox = -1
                    else: # We quit the last menu
                        menus = []
                        screen.QuitMenu(menu_index, selection_id)
                        return choice

def MovementLoop(current_character, screen):
    """Action Loop: current_character move on the map
    current_character - character
    screen - screen"""
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
                if event.key in [K_UP, K_DOWN, K_RIGHT, K_LEFT]:
                    # We move the current character
                    IfDeplacement(current_character, event.key, screen)

            elif event.type == MOUSEMOTION:
                screen.onHover(event.pos)

def PlacementLoop(ini_tiles, screen):
    """Action Loop: the player pos it's character on the map
    ini_tiles - list of tuple of two int
    screen - screen"""
    highlighted = Highlight.HighlightTiles(screen._tile_size, ini_tiles,60, (0, 0,255))
    blue, red = {}, [False, False]
    for pos in highlighted:
        blue[pos] = screen.AddHighlight(highlighted[pos])
    l = list(blue.keys())
    selection = 0
    selection_menu = 0
    s = Highlight.HighlightTiles(screen._tile_size,[l[selection]], 120, (255, 0, 0))
    red = [screen.AddHighlight(s[l[selection]]), l[selection]]

    mainClock = pygame.time.Clock()
    characters = {}
    menu_open = False
    j = False
    available = []
    for i, character in enumerate(screen._characters):
        if character._team == 1:
            screen._charBox = i
            available.append(character)
    max_chara = len(available)
    while True:
        screen.refresh()
        mainClock.tick(30)
        change = False
        for event in pygame.event.get():
            if event.type == QUIT:  # The game is closed
                pygame.quit()
                sys.exit()

            elif event.type == KEYDOWN:
                if menu_open:
                    if event.key == K_RETURN:
                        characters[l[screen._charBox]] = screen._characters[screen._charBox]
                        screen._characters[screen._charBox].UpdatePos(screen._tile_size, pos_tile = l[selection])
                        screen._characters[screen._charBox]._index = screen.AddCharacter(screen._characters[screen._charBox], 'standing')
                        change = True
                        for i, character in enumerate(available):
                            if character == screen._characters[screen._charBox]:
                                available.pop(i)
                                break
                        if len(available) == 0:
                            screen.RemoveObject(red[0])
                            for tile in list(blue.values()) + screen._ui['childBox']:
                                screen.RemoveObject(tile)
                            screen._ui['childBox'] = []
                            screen.QuitMenu(menu_index, selection_id)
                            screen._charBox = -1
                            return characters
                        screen._charBox = (screen._charBox+1)%len(l)
                        while screen._characters[screen._charBox]._team == 1:
                            screen._charBox = (screen._charBox+1)%len(l)
                        event.key = K_ESCAPE
                    elif event.key in [K_UP, K_DOWN]:  # We navigate through the menu
                        selection_menu, selection_id = screen.MenuNavigation(event.key, menu_index, selection_menu, selection_id)
                    elif event.key in [K_RIGHT, K_LEFT]:
                        screen.QuitMenu(menu_index, selection_id)
                        if event.key == K_RIGHT:
                            j = -1
                        else:
                            j = 1
                        screen._charBox = (screen._charBox+j)%len(screen._characters)
                        while screen._characters[screen._charBox] not in available:
                            screen._charBox = (screen._charBox+j)%len(screen._characters)
                        menu_index, selection_id = screen.OpenMenu('Status')

                    if event.key == K_ESCAPE:
                        for index in screen._ui['childBox']:
                            screen.RemoveObject(index)
                        screen._ui['childBox'] = []
                        screen.QuitMenu(menu_index, selection_id)
                        screen._charBox = -1
                        menu_open = False
                else:
                    if event.key == K_RETURN:
                        if l[selection] in [character._tile for character in screen._characters]:
                            for character in screen._characters:
                                if character._tile == l[selection]:
                                    available.append(character)
                                    character.UpdatePos(screen._tile_size)
                                    for index in character._index:
                                        screen.RemoveObject(index)
                        else:
                            screen._charBox = 1
                            while screen._characters[screen._charBox] not in available:
                                screen._charBox = (screen._charBox+1)%len(screen._characters)
                            menu_index, selection_id = screen.OpenMenu('Status')
                            menu_open = True
                    elif event.key == K_RIGHT:
                        selection = (selection+1)%len(l)
                        change = True
                    elif event.key == K_LEFT:
                        selection = (selection-1)%len(l)
                        change = True
                    elif event.key == K_ESCAPE and len(available)!=max_chara:
                        screen.RemoveObject(red[0])
                        for tile in blue:
                            screen.RemoveObject(blue[tile])
                        return characters
            elif event.type == MOUSEMOTION and not menu_open:
                mouse_pos = screen.onHover(event.pos)
                for i, tile in enumerate(l):
                    if mouse_pos == tile:
                        print(mouse_pos)
                        selection = i
                        change = True
                        break
            if change:
                change = False
                screen.RemoveObject(red[0])
                s = Highlight.HighlightTiles(screen._tile_size,[l[selection]],
                                             120, (255, 0, 0))
                red = [screen.AddHighlight(s[l[selection]]), l[selection]]


def VNLoop(screen, lines):
    """Action Loop: visual novel part
    screen - screen
    lines - list of string: lines of the script"""
    on_screen = {}
    mainClock = pygame.time.Clock()
    for line in lines:
        change = False
        if ':' in line:  # This is a declaration
            box = TextBox.Dialog(util.FormatText(line, 42))
            pos = (int((screen._size[0]-box._size[0])/2),screen._size[1]-box._size[1])
            current_dialog = screen.AddTextBox(box, pos)
        else:  # A character enter or leave
            change = True
            line = line.split()
            if line[0] == 'enter':
                character, file, transf, pos = line[1:]
                x, y = tuple([int(ele) for ele in pos.split(',')])
                if x < 0:
                    x = screen._size[0]+x
                if y < 0:
                    y = screen._size[1]+y
                img = pygame.image.load(join('res', 'sprite',
                                        file.split('_')[0], file))
                if transf == 'sym':
                    sprite = pygame.transform.flip(img, True, False)
                else:
                    sprite = img
                on_screen[character] = screen.AddSprite(sprite, (x, y))
            elif line[0] == 'leave':
                screen.RemoveObject(on_screen[line[1]])
        while change == False:
            screen.refresh()
            mainClock.tick(30)
            for event in pygame.event.get():
                if event.type == QUIT:  # The game is closed
                    pygame.quit()
                    sys.exit()
                if event.type == KEYDOWN:
                    if event.key == K_RETURN:
                        change = True
                        [screen.RemoveObject(index) for index in current_dialog]
    [screen.RemoveObject(i) for i in current_dialog + list(on_screen.values())]
    print('Dialog end')

