import Character
import Team
import Screen
import pygame
import sys
from MainGame import *

class Level():
    def __init__(self, map_data, screen, playerTeam, opponentTeam, teams):
        self._map_data = map_data
        self._screen = screen
        self._playerTeam = playerTeam
        self._opponentTeam = opponentTeam
        self._teams = teams

    def CheckVictoryCondition(self):
        playerVictory, opponentVictory = True, True
        print(self._opponentTeam._members, self._playerTeam._members)
        if self._victory_condition == 'destroy':
            for character in self._opponentTeam._members:
                if not character._dead:
                    playerVictory = False
            for character in self._playerTeam._members:
                if not character._dead:
                    opponentVictory = False
        if playerVictory:
            print('You win')
            self._screen.refresh()
            sys.exit()
        if opponentVictory:
            print('Game Over')
            self._screen.refresh()
            sys.exit()

    def ModeTRPG(self):

        turns, turn = IniTurns(self._screen._characters)
        character = turns[turn]
        self._screen.MoveCircle(pos = character._pos)
        self._screen.UpdateStatus(turns[turn], (self._screen._height-128, self._screen._width-100))

        pygame.display.update()  # Initial display
        self._screen.refresh()
        while True:
            menu = MovementLoop(character, self._screen, self._map_data)
            if character._cara['PA'] == 0 and character._cara['PM'] == 0 :
                turn = NextTurn(self._screen, turns, turn)
                character = turns[turn]
            if character._team_number == 1:
                current_team = self._playerTeam
            elif character._team_number == 2:
                current_team = self._opponentTeam
            menu = MenusLoop(menu, character, self._screen, self._map_data, current_team)
            if menu == 'End Turn' or (character._cara['PA'] == 0 and character._cara['PM'] == 0) or character._dead:
                turn = NextTurn(self._screen, turns, turn)
                character = turns[turn]
            self.CheckVictoryCondition()

class Level_0(Level):
    def __init__(self):
        screen_height, screen_width = (640,640)
        tile_size = 29
        screen = Screen.Screen(screen_height, screen_width, tile_size)
        map_index = screen.AddMap("TestLevel.tmx")
        map_data = screen._objects[map_index][0].renderer.tmx_data

        characters = [('Anna', (2,2), 1), ('Henry', (3, 3), 2)]
        playerTeam, opponentTeam = [], []
        for character in characters:
            temp = Character.Character.Initialization(character[0], screen._tile_size, character[1], character[2])
            temp._index = screen.AddCharacter(temp, 'standing')
            if character[2] == 1:
                playerTeam.append(temp)
            elif character[2] == 2:
                opponentTeam.append(temp)
        playerTeam = Team.Team(1, playerTeam, screen._tile_size)
        opponentTeam = Team.Team(2, opponentTeam, screen._tile_size)
        playerTeam._team_opponent.append(opponentTeam._number)
        opponentTeam._team_opponent.append(playerTeam._number)
        teams = [playerTeam, opponentTeam]
        playerTeam.relations(teams)
        opponentTeam.relations(teams)

        screen.SetCharacters(teams)
        Level.__init__(self, map_data, screen, playerTeam, opponentTeam, teams)
        self._victory_condition = 'destroy'
