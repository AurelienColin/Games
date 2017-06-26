import Highlight
import Map
import numpy as np
import util
import Effect
import random
from os.path import join
import pyganim
import pygame
import json

class Skill():
    def __init__(self, file):
        self.FromJSON(file)
        self._sprite = self.AddSprite('fire_4', 1, 11, 0, 10)

    def FromJSON(self, file):
        print(file)
        with open(join('..', 'res','json', 'skill', file+'.json'), 'r') as file:
            data = json.load(file)['skill']
        self._cara = data['cara']
        self._sprite = {'values': data['sprite']}
        self._sheet_name = data['sheet']
        self.CreateSprite()
        self._effects = {'values':data['effects'], 'effects':[]}
        if self._effects['values']:
            for e in self._effects['values']:
                    print(e, type(e))
                    effect = Effect.Effect(e['type'], e['power'], e['duration'])
                    print(effect)
                    self._effects['effects'].append(effect)
            print(self._effects['effects'])

    def ToJSON(self):
        """Write the character in a .json
        Input :
        self - a character

        Output :
        Nothing, but a .json est written"""
        temp = {'cara':self._cara, 'sprite':self._sprite['values'],
                'sheet':self._sheet_name, 'effects':self._effects}
        util.WriteJSON({'character':temp}, self._cara['name'])

    def CreateSprite(self):
        name = self._sheet_name
        rows = self._sprite['values']['rows']
        cols = self._sprite['values']['cols']
        begin, end = self._sprite['values']['action']
        self._sprite['action'] = self.AddSprite(name, rows, cols, begin, end)
        pass

    def AddSprite(self, name, rows, cols, begin, end):
        """Make a sprite (animated or not) from a sheet

        Output:
        obj - a sprite"""
        fullname = join('..', 'res', 'sprite', 'effect', name + '.png')
        perso = pyganim.getImagesFromSpriteSheet(fullname,cols=cols,rows=rows)[begin:end]
        if end > begin+1:
            frames = list(zip(perso, [100]*(end-begin)))
            obj = pyganim.PygAnimation(frames)
            obj.play()
        else:
            obj = perso[0]
        return obj

    def Aim(self, character, screen):
        """Return the tiles aimed by the skill
        Input:
        self - skill
        character - character: the one using the skill
        screen - screen

        Output:
        blue - dictionary
            key - tuple of two int
            value - highlight"""
        center = (int(character._pixel[0]/screen._tile_size),
                  int(character._pixel[1]/screen._tile_size))

        aimable = self.GetAimable(center,screen, character)
        highlighted = Highlight.HighlightTiles(screen._tile_size, aimable,60, (0, 0,255))
        blue = {}
        for pos in highlighted:
            blue[pos] = screen.AddHighlight(highlighted[pos])
        return blue

    def AOE(self, tile_pos, character, screen):
        """Return the tiles included in the AOE
        Input:
        self - skill
        tile_pos - tuple of two int: center of the AOE
        character - character using the skill
        screen - screen

        Output:
        final_tiles - list of tuple of two int"""
        tiles = [tile_pos]
        if self._cara['size'] == 1:
            pass
        elif not self._cara['AOE']:
            for i in range(self._cara['size']):
                j = 0
                while j+i < self._cara['size']:
                    tiles.append([tile_pos[0]-i, tile_pos[1]-j])
                    tiles.append([tile_pos[0]+i, tile_pos[1]-j])
                    tiles.append([tile_pos[0]-i, tile_pos[1]+j])
                    tiles.append([tile_pos[0]+i, tile_pos[1]+j])
                    j+=1
        elif self._cara['AOE'] == 'parallel':
            if tile_pos[0] != character._tile[0]:
                for i in range(self._cara['size']):
                    tiles.append([tile_pos[0], tile_pos[1]+i])
                    tiles.append([tile_pos[0], tile_pos[1]-i])
            elif tile_pos[1] != character._tile[1]:
                for i in range(self._cara['size']):
                    tiles.append([tile_pos[0]+i, tile_pos[1]])
                    tiles.append([tile_pos[0]-i, tile_pos[1]])
        elif self._cara['AOE'] == 'orthogonal':
            if tile_pos[0] != character._tile[0]:
                for i in range(self._cara['size']):
                    tiles.append([tile_pos[0]-i, tile_pos[1]])
                    tiles.append([tile_pos[0]+i, tile_pos[1]])
            elif tile_pos[1] != character._tile[1]:
                for i in range(self._cara['size']):
                    tiles.append([tile_pos[0], tile_pos[1]+i])
                    tiles.append([tile_pos[0], tile_pos[1]-i])
        final_tiles = []
        for tile in tiles:
            if tile not in final_tiles:
                final_tiles.append(tuple(tile))
        return final_tiles

    def Affect(self, current_character, all_affected, tiles, screen):
        """Use the skill and apply it's effect on the targets
        Input:
        self - skill
        current_character - character
        all_affected - list of character
        tiles - list of tuple of two int (target of the skill)
        screen - screen

        Output:
        xp - int: xp earn from the attack
        The effects are applied on the targets (character or tile)"""
        xp = 0
        animation_tiles = []
        for i, affected in enumerate(all_affected):
            cara = affected._cara
            w, s = util.WeakAgainst(cara['type'])
            tile_type = Map.CheckProperties(affected._tile, 'type',
                                            screen._map_data, screen._tile_size)
            if tile_type == w:
                affected._cara['def'] -= 56
                affected._cara['avoid'] -= 56
                affected._cara['speed'] -= 56
                affected._cara['resistance'] -= 56
                affected._cara['elementalRes'][w] -= 56
            elif tile_type == cara['type']:
                affected._cara['def'] += 56
                affected._cara['avoid'] += 56
                affected._cara['speed'] += 56
                affected._cara['resistance'] += 56
                affected._cara['elementalRes'][w] += 56
            else:
                w, s = util.WeakAgainst(tile_type)
                if w:
                    affected._cara['elementalRes'][w] -= 23
                    affected._cara['elementalRes'][s] += 23


            if current_character._aiming == affected._tile:
                direction = util.GetDirection(affected._tile, current_character._tile)
            else:
                direction = util.GetDirection(affected._tile, current_character._aiming)
            if direction - affected._direction in [-2,2]:
                dmg = self._cara['damage'] * 1.5
                affected._cara['avoid'] = int(affected._cara['avoid']*0.75)
            elif direction - affected._direction in [-3,-1,1,3]:
                dmg = self._cara['damage'] * 1.25
                affected._cara['avoid'] = int(affected._cara['avoid']*0.5)
            else:
                dmg = self._cara['damage']
            if self._cara['type'] == 'magic':
                dmg = current_character.MagicalDmg(dmg)
                dmg = affected.MagicalReduction(dmg, self._cara['ele'])
            elif self._cara['type'] == 'physic':
                dmg = current_character.PhysicalDmg(dmg)
                dmg = affected.PhysicalReduction(dmg, self._cara['ele'])
            else:    # skill._type == 'heal'
                dmg = -current_character.MagicalDmg(self._cara['damage'])
            hit = affected.getCara('avoid')/current_character.getCara('hit')*self._cara['hit']
            r = random.random()
            affected._cara = cara
            if r < hit:
                animation_tiles.append(affected._tile)
                xp += affected.Affect(dmg, screen)
                print('effects:', self._effects)
                for effect in self._effects['effects']:
                    xp += affected.Affect(effect, screen)
        animations = []
        print('launch animation to:', animation_tiles)
        for tile in animation_tiles:
            pos = tuple(x*screen._tile_size for x in tile)
            print('indeed:', pos)
            animations.append(screen.AddSprite(self._sprite, pos))
        if animations != []:
            mainClock = pygame.time.Clock()
            for i in range(25):
                screen.refresh(force = True)
                mainClock.tick(100)
            [screen.RemoveObject(index) for index in animations]

        return xp

    def GetAimable(self, pos, screen, current_character):
        """
        Input:
        self - skill
        pos - tuple of two int: origin of the attack
        screen - screen
        current_character - character using the attack

        Output:
        list of tuple of two int"""
        map_data, tile_size = screen._map_data, screen._tile_size
        aimable = set()
        scope = self._cara['range']
        p = 'slowness'
        for x in range(max(pos[0]-scope, 0), pos[0]+scope+1):
            diff_x = x-pos[0]
            for y in range(max(pos[1]-scope,0), pos[1]+scope+1):
                diff_y = y-pos[1]
                transparent = True

                if (self._cara['AOE'] == 'parallel' or self._cara['AOE'] == 'orthogonal') and (x != pos[0] and y!= pos[1]):
                    transparent = False
                elif abs(diff_x) + abs(diff_y) > scope:
                    transparent = False
                elif Map.CheckProperties((x*tile_size, y*tile_size), p, map_data, tile_size) != '1':
                    transparent = False
                elif diff_y != 0 or diff_x != 0:
                    R = abs(diff_y)+abs(diff_x)
                    y_step = diff_y/R
                    x_step = diff_x/R
                    if x_step != 0:
                        x_range = np.arange(pos[0], x, x_step)
                    else:
                        x_range = [x for i in range(R+1)]
                    if y_step != 0:
                        y_range = np.arange(pos[1], y, y_step)
                    else:
                        y_range = [y for i in range(R+1)]
                    tile_range = [(int(x_range[i]+0.5), int(y_range[i]+0.5)) for i in range(R)]
                    for x_c, y_c in tile_range:
                        if not self._cara['perce']:
                            for character in screen._characters:
                                if character._tile == (x_c, y_c) and character._team != current_character._team:
                                    transparent = False
                                    break
                        if Map.CheckProperties((x_c*tile_size, y_c*tile_size), p, map_data, tile_size) != '1':
                            transparent = False
                            break
                if transparent:
                    aimable.add((x, y))
        current_character._aiming = pos
        return list(aimable)


def ListSkills():
    return set(['Horizontal', 'Vertical', 'Execution', 'Apocalypse'])
