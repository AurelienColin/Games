import Highlight
import Map
import numpy as np
import util
import Effect
import random

class Skill():
    def __init__(self):
        self._char_effects = {}
        self._damage = 0
        self._heal = 0
        self._hit = 0.8
        self._tile_effects = {}
        self._ele = 'neutral'

    def Initialization(name):
        """
        Input:
        name - string

        Output:
        self - skill"""
        if name == 'Execution':
            self = Execution()
        elif name == 'Vertical':
            self = Vertical()
        elif name == 'Horizontal':
            self = Horizontal()
        elif name == 'Apocalypse':
            self = Apocalypse()
        else:
            self = None
        return self

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
        center = (int(character._pos[0]/screen._tile_size),
                  int(character._pos[1]/screen._tile_size))

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
        if self._size == 1:
            pass
        elif not self._AOE:
            for i in range(self._size):
                j = 0
                while j+i < self._size:
                    tiles.append([tile_pos[0]-i, tile_pos[1]-j])
                    tiles.append([tile_pos[0]+i, tile_pos[1]-j])
                    tiles.append([tile_pos[0]-i, tile_pos[1]+j])
                    tiles.append([tile_pos[0]+i, tile_pos[1]+j])
                    j+=1
        elif self._AOE == 'parallel':
            if tile_pos[0] != character._pos_tile[0]:
                for i in range(self._size):
                    tiles.append([tile_pos[0], tile_pos[1]+i])
                    tiles.append([tile_pos[0], tile_pos[1]-i])
            elif tile_pos[1] != character._pos_tile[1]:
                for i in range(self._size):
                    tiles.append([tile_pos[0]+i, tile_pos[1]])
                    tiles.append([tile_pos[0]-i, tile_pos[1]])
        elif self._AOE == 'orthogonal':
            if tile_pos[0] != character._pos_tile[0]:
                for i in range(self._size):
                    tiles.append([tile_pos[0]-i, tile_pos[1]])
                    tiles.append([tile_pos[0]+i, tile_pos[1]])
            elif tile_pos[1] != character._pos_tile[1]:
                for i in range(self._size):
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
        for affected in all_affected:
            cara = affected._cara
            w, s = util.WeakAgainst(cara['type'])
            tile_type = Map.CheckProperties(affected._pos_tile, 'type',
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


            if current_character._aiming == affected._pos_tile:
                direction = util.GetDirection(affected._pos_tile, current_character._pos_tile)
            else:
                direction = util.GetDirection(affected._pos_tile, current_character._aiming)
            if direction - affected._direction in [-2,2]:
                dmg = self._damage * 1.5
                affected._cara['avoid'] = int(affected._cara['avoid']*0.75)
            elif direction - affected._direction in [-3,-1,1,3]:
                dmg = self._damage * 1.25
                affected._cara['avoid'] = int(affected._cara['avoid']*0.5)
            else:
                dmg = self._damage
            if self._type == 'magic':
                dmg = current_character.MagicalDmg(dmg)
                dmg = affected.MagicalReduction(dmg, self._ele)
            elif self._type == 'physic':
                dmg = current_character.PhysicalDmg(dmg)
                dmg = affected.PhysicalReduction(dmg, self._ele)
            else:    # skill._type == 'heal'
                dmg = -current_character.MagicalDmg(self._damage)
            hit = affected.getCara('avoid')/current_character.getCara('hit')*self._hit
            r = random.random()
            affected._cara = cara
            if r < hit:
                affected.Affect(dmg, screen)
                for effect in self._char_effects:
                    r = ['PA', 'PM']
                    if effect._properties in r and random.random() < affected.getCara('res'+effect._properties):
                        xp += affected.Affect(effect, screen)
                    else:
                        xp += affected.Affect(effect, screen)
        for effect in self._tile_effects:
            for tile in tiles:
                screen._tile_effect.append([tile, effect])
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
        scope = self._range
        p = 'slowness'
        for x in range(max(pos[0]-scope, 0), pos[0]+scope+1):
            diff_x = x-pos[0]
            for y in range(max(pos[1]-scope,0), pos[1]+scope+1):
                diff_y = y-pos[1]
                transparent = True

                if (self._AOE == 'parallel' or self._AOE == 'orthogonal') and (x != pos[0] and y!= pos[1]):
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
                        if not self._perce:
                            for character in screen._characters:
                                if character._pos_tile == (x_c, y_c) and character._team != current_character._team:
                                    transparent = False
                                    break
                        if Map.CheckProperties((x_c*tile_size, y_c*tile_size), p, map_data, tile_size) != '1':
                            transparent = False
                            break
                if transparent:
                    aimable.add((x, y))
        current_character._aiming = pos
        return list(aimable)



class Horizontal(Skill):
    def __init__(self):
        Skill.__init__(self)
        self._name = 'Horizontal'
        self._AOE = 'parallel'
        self._size = 2
        self._cost = 4
        self._damage = 10
        self._range = 2
        self._sprite_sheet = None
        self._perce = False
        self._type = 'physic'

class Vertical(Skill):
    def __init__(self):
        Skill.__init__(self)
        self._name = 'Vertical'
        self._AOE = 'orthogonal'
        self._size = 2
        self._cost = 4
        self._damage = 20
        self._range = 3
        self._sprite_sheet = None
        self._perce = False
        self._type = 'physic'

class Execution(Skill):
    def __init__(self):
        Skill.__init__(self)
        self._name = 'Execution'
        self._AOE = None
        self._size = 1
        self._cost = 3
        self._damage = 30
        self._range = 5
        self._sprite_sheet = None
        self._perce = False
        self._type = 'physic'

class Apocalypse(Skill):
    def __init__(self):
        Skill.__init__(self)
        self._name = 'Apocalypse'
        self._AOE = None
        self._size = 2
        self._cost = 4
        self._damage = 10
        self._range = 5
        self._sprite_sheet = None
        self._perce = False
        self._char_effects = [Effect.Effect('PA', 1, 2)]
        self._tile_effects = [Effect.Effect('PV', 1, 5)]
        self._type = 'physic'

def ListSkills():
    return set(['Horizontal', 'Vertical', 'Execution', 'Apocalypse'])