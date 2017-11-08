from . import Loop, util, Effect, Screen, Highlight
import pygame
import sys
from os.path import join
import json

class Level():
    def __init__(self, screen, file):
        screen.Clean()
        with open(join('res','json', 'level', file+'.json'), 'r') as file:
            data = json.load(file)['level']
        mapIndex = screen.AddMap(data['map'])
        screen.mapData = screen.objects[mapIndex][0].renderer.tmx_data

        self.screen = screen

        self.ModeVN(data['script'])
        chars = data['characters']
        screen.IniChar(chars)

        iniTiles = data['initial_tiles']
        self.music = pygame.mixer.Sound(join('res', 'music', data['music']['placement']))
        self.music.play(loops=-1)
        Loop.PlacementLoop(iniTiles, self.screen)
        self.music.stop()
        
        self.music = pygame.mixer.Sound(join('res', 'music', data['music']['TRPG']))
        self.music.play(loops=-1)
        self.victories = data['victories']
        self.ModeTRPG()

    def CheckVictoryCondition(self):
        """Check if a victory is fulfilled
        Currently implemented : destroy, kill leaders

        Output:
        sys.exit if a condition is fulfilled"""
        opponentVictory = True
        for char in self.screen.characters:
            if char.team == 1 and char.leader and not char.dead:
                opponentVictory = False
        if opponentVictory:
            self.screen.refresh()
            self.music.stop()
            sys.exit()

        for victory in self.victories:
            playerVictory = True
            nextLevel = victory['next_level']
            if victory['condition'] == 'destroy':
                for char in self.screen.characters:
                    if not char.dead and char.team == 2:
                        playerVictory = False
            elif victory['condition'] == 'kill leaders':
                for char in self.screen.characters:
                    if not char.dead and char.team == 2 and char.leader:
                        playerVictory = False
            if playerVictory:
                print('You win')
                self.music.stop()
                self = Level(self.screen, nextLevel)

    def ModeTRPG(self):
        """Launch action loop for a tactical RPG"""
        turns, turn = self.IniTurns()
        char = turns[turn]

        pygame.display.update()  # Initial display
        self.screen.refresh()
        while True:
            menu = Loop.MovementLoop(char, self.screen)
            if char.cara['PA'] == 0 and char.cara['PM'] == 0 :
                turn = self.NextTurn(turns, turn)
                char = turns[turn]
            menu = Loop.MenusLoop(menu, self.screen, char=char)
            if menu == 'End Turn' or (char.cara['PA'] == 0 and char.cara['PM'] == 0) or char.dead:
                turn = self.NextTurn(turns, turn)
                char = turns[turn]
            self.CheckVictoryCondition()

    def ModeVN(self, filename):
        """Launch action loop for a visual novel"""
        fullname = join('res', 'script', filename)
        file = open(fullname)
        lines = file.readlines()
        file.close()
        Loop.VNLoop(self.screen, lines)


    def IniTurns(self):
        """Initialization of turns

        Output:
        turns - a dictionary
            key - int: speed factor of the char
            value - char"""
        self.screen.characters.sort(key=lambda x: x.cara['speed'], reverse=True)
        turns = {}
        for char in self.screen.characters:
            speed = int(util.StatCalculation(char.cara['speed'])*100)
            while speed in turns:
                speed += 1
            turns[speed] = char
        turn = min(turns)

        self.screen.MoveCircle(pos = turns[turn].pos['px'])
        self.screen.UpdateStatus(turns[turn])
        self.screen.UpdateIniList(turns, turn)
        if turns[turn].ia:
            turns[turn].IA_Action(self.screen)
            self.CheckVictoryCondition()
            return self.NextTurn(turns, turn)
        return turns, turn

    def NextTurn(self, turns, turn):
        """Update turns

        Output:
        turns - char: next char to play"""
        if not turns[turn].dead:
            speed = turn + int(util.StatCalculation(turns[turn].cara['speed'])*100)
            while speed in turns:
                speed += 1
            turns[speed] = turns[turn]
        turn+=1
        while turn not in turns or turns[turn].dead:
            turn +=1
        turns[turn].passTurn()
        effects = {}
        for i, tileEffect in enumerate(self.screen.tileEffects):
            pos, effect = tileEffect
            charEffect = Effect.Effect(effect.properties, effect.power, 1)
            if turns[turn].pos['tile'] == pos:
                turns[turn].Affect(charEffect, self.screen)
            if effect not in effects:
                effects[effect]=[i]
            else:
                effects[effect].append(i)
        for effect, i in effects.items():
            if effect.since != effect.duration:
                effect.since += 1
            else:
                for j in i:
                    self.screen.tileEffects[j] = None
        self.screen.tileEffects = [effect for effect in self.screen.tileEffects if effect]

        self.screen.MoveCircle(pos = turns[turn].pos['px'])
        self.screen.UpdateStatus(turns[turn])
        self.screen.UpdateIniList(turns, turn)
        if turns[turn].ia:
            turns[turn].IA_Action(self.screen)
            self.CheckVictoryCondition()
            return self.NextTurn(turns, turn)
        return turn
