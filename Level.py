import Character
import Screen
import pygame
import sys
from MainGame import *

class Level():
    def __init__(self, screen):
        self._map_data = screen._map_data
        self._screen = screen

    def CheckVictoryCondition(self):
        playerVictory, opponentVictory = True, True
        for character in self._screen._characters:
            if character._team == 1 and character._leader and not character._dead:
                opponentVictory = False
        if self._victory_condition == 'destroy':
            for character in self._screen._characters:
                if not character._dead and character._team == 2:
                    playerVictory = False
        elif self._victory_condition == 'kill leaders':
            for character in self._scree._characters:
                if not character._dead and character._team == 2 and character._leader:
                    playerVictory = False
        if playerVictory:
            print('You win')
            self._screen.refresh()
            sys.exit()
        if opponentVictory:
            print('Game Over')
            self._screen.refresh()
            sys.exit()

    def ModeTRPG(self):
        turns, turn = self.IniTurns()
        character = turns[turn]

        pygame.display.update()  # Initial display
        self._screen.refresh()
        while True:
            menu = MovementLoop(character, self._screen)
            if character._cara['PA'] == 0 and character._cara['PM'] == 0 :
                turn = self.NextTurn(turns, turn)
                character = turns[turn]
            menu = MenusLoop(menu, character, self._screen)
            if menu == 'End Turn' or (character._cara['PA'] == 0 and character._cara['PM'] == 0) or character._dead:
                turn = self.NextTurn(turns, turn)
                character = turns[turn]
            self.CheckVictoryCondition()


    def IniTurns(self):
        self._screen._characters.sort(key=lambda x: x._cara['speed'], reverse=True)
        turns = {}
        for character in self._screen._characters:
            speed = int(util.StatCalculation(character._cara['speed'])*100)
            while speed in turns:
                speed += 1
            turns[speed] = character
        turn = min(turns)

        self._screen.MoveCircle(pos = turns[turn]._pos)
        self._screen.UpdateStatus(turns[turn], (self._screen._height-128, self._screen._width-100))
        self._screen.UpdateIniList(turns, turn)
        if turns[turn]._ia:
            turns[turn].IA_Action(self._screen)
            self.CheckVictoryCondition()
            return self.NextTurn(turns, turn)
        return turns, turn

    def NextTurn(self, turns, turn):
        if not turns[turn]._dead:
            speed = turn + int(util.StatCalculation(turns[turn]._cara['speed'])*100)
            while speed in turns:
                speed += 1
            turns[speed] = turns[turn]
        turn+=1
        while turn not in turns or turns[turn]._dead:
            turn +=1
        turns[turn].passTurn()

        for i, pos_effect in enumerate(self._screen._tile_effect):
            if pos_effect:
                pos, effect = pos_effect
                char_effect = Effect.Effect(effect._properties, effect._power, 1)
                if turns[turn]._pos_tile == pos:
                        turns[turn].Affect(char_effect, self._screen)
                        break
                if effect._since != effect._duration:
                    self._screen._tile_effect[i][1]._since += 1
                else:
                    self._screen._tile_effect.pop(i)

        self._screen.MoveCircle(pos = turns[turn]._pos)
        self._screen.UpdateStatus(turns[turn])
        self._screen.UpdateIniList(turns, turn)
        if turns[turn]._ia:
            turns[turn].IA_Action(level._screen)
            level.CheckVictoryCondition()
            return self.NextTurn(turns, turn)
        return turn

class Level_0(Level):
    def __init__(self, screen):
        map_index = screen.AddMap("TestLevel.tmx")
        screen._map_data = screen._objects[map_index][0].renderer.tmx_data
        Level.__init__(self, screen)

        characters = [('Anna', None, 1, False, True),
                      ('Henry', (3, 3), 2, False, True)]
        screen.IniChar(characters)

        ini_tiles = [(4, 4), (10, 5), (3, 2)]
        PlacementLoop(ini_tiles, self._screen)

        self._victory_condition = 'destroy'
