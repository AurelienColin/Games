from . import Loop, util, Effect, Screen
import pygame
import sys
from os.path import join
import json

class Level():
    def __init__(self, screen, file):
        screen.Clean()
        with open(join('res','json', 'level', file+'.json'), 'r') as file:
            data = json.load(file)['level']
        map_index = screen.AddMap(data['map'])
        screen._map_data = screen._objects[map_index][0].renderer.tmx_data

        self._screen = screen

        self.ModeVN(data['script'])
        characters = data['characters']
        screen.IniChar(characters)

        ini_tiles = data['initial_tiles']
        Loop.PlacementLoop(ini_tiles, self._screen)
        self._victories = data['victories']
        self.ModeTRPG()

    def CheckVictoryCondition(self):
        """Check if a victory is fulfilled
        Currently implemented : destroy, kill leaders

        Output:
        sys.exit if a condition is fulfilled"""
        opponentVictory = True
        for character in self._screen._characters:
            if character._team == 1 and character._leader and not character._dead:
                opponentVictory = False
        if opponentVictory:
            print('Game Over')
            self._screen.refresh()
            sys.exit()

        for victory in self._victories:
            playerVictory = True
            next_level = victory['next_level']
            if victory['condition'] == 'destroy':
                for character in self._screen._characters:
                    if not character._dead and character._team == 2:
                        playerVictory = False
            elif victory['condition'] == 'kill leaders':
                for character in self._scree._characters:
                    if not character._dead and character._team == 2 and character._leader:
                        playerVictory = False
            if playerVictory:
                print('You win')
                self = Level(self._screen, next_level)

    def ModeTRPG(self):
        """Launch action loop for a tactical RPG"""
        turns, turn = self.IniTurns()
        character = turns[turn]

        pygame.display.update()  # Initial display
        self._screen.refresh()
        while True:
            menu = Loop.MovementLoop(character, self._screen)
            if character._cara['PA'] == 0 and character._cara['PM'] == 0 :
                turn = self.NextTurn(turns, turn)
                character = turns[turn]
            menu = Loop.MenusLoop(menu, self._screen, current_character=character)
            if menu == 'End Turn' or (character._cara['PA'] == 0 and character._cara['PM'] == 0) or character._dead:
                turn = self.NextTurn(turns, turn)
                character = turns[turn]
            self.CheckVictoryCondition()

    def ModeVN(self, filename):
        """Launch action loop for a visual novel"""
        fullname = join('res', 'script', filename)
        file = open(fullname)
        lines = file.readlines()
        file.close()
        Loop.VNLoop(self._screen, lines)


    def IniTurns(self):
        """Initialization of turns

        Output:
        turns - a dictionary
            key - int: speed factor of the character
            value - character"""
        self._screen._characters.sort(key=lambda x: x._cara['speed'], reverse=True)
        turns = {}
        for character in self._screen._characters:
            speed = int(util.StatCalculation(character._cara['speed'])*100)
            while speed in turns:
                speed += 1
            turns[speed] = character
        turn = min(turns)

        self._screen.MoveCircle(pos = turns[turn]._pixel)
        self._screen.UpdateStatus(turns[turn])
        self._screen.UpdateIniList(turns, turn)
        if turns[turn]._ia:
            turns[turn].IA_Action(self._screen)
            self.CheckVictoryCondition()
            return self.NextTurn(turns, turn)
        return turns, turn

    def NextTurn(self, turns, turn):
        """Update turns

        Output:
        turns - character: next character to play"""
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
                if turns[turn]._tile == pos:
                        turns[turn].Affect(char_effect, self._screen)
                        break
                if effect._since != effect._duration:
                    self._screen._tile_effect[i][1]._since += 1
                else:
                    self._screen._tile_effect.pop(i)

        self._screen.MoveCircle(pos = turns[turn]._pixel)
        self._screen.UpdateStatus(turns[turn])
        self._screen.UpdateIniList(turns, turn)
        print('ia:', turns[turn]._ia)
        if turns[turn]._ia:
            turns[turn].IA_Action(self._screen)
            self.CheckVictoryCondition()
            return self.NextTurn(turns, turn)
        return turn
