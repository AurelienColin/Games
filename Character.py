import pyganim
from os.path import join
import Highlight
import Skill
import pygame
import util
import Map

from random import uniform

class Character():
    def __init__(self, ia):
        self._sprite = {}
        self._cara = {}
        self._index = None
        self._lifebar1 = None
        self._lifebar2 = None
        self._pos = None
        self._pos_tile = None
        self._index = None
        self._xp_on_damage = 0
        self._xp_on_kill = 0
        self._xp = 0
        self._dead = False
        self._ia = ia
        self._team = 0

        self._skills = []
        self._cara['PV'], self._cara['PV_max'] = 0, 0
        self._cara['PA'], self._cara['PA_max'] = 0, 0
        self._cara['PM'], self._cara['PM_max'] = 0, 0
        self._cara['speed'] = 1
        self._cara['magic'] = 1
        self._cara['strength'] = 1
        self._cara['defense'] = 1
        self._cara['resistance'] = 1
        self._cara['effects'] = [False]
        self._cara['elementalRes'] = {'fire':0, 'water':0, 'earth':0,
                                      'wind':0, 'holy':0, 'unholy':0,
                                      'neutral':0}


    def Initialization(name, tile_size, pos_tile, team, ia = False):
        if name == 'Anna':
            self = Anna(tile_size, pos_tile, ia)
        elif name == 'Henry':
            self = Henry(tile_size, pos_tile, ia)
        else:
            self = None
        self._team = team
        return self

    def AddSprite(self, begin, end=False):
        if not end:
            end = begin+1
        fullname = join('res', 'sprite', str(self._id) + '.png')
        perso = pyganim.getImagesFromSpriteSheet(fullname,cols=self._cols,rows= self._rows)[begin:end]
        if end > begin+1:
            frames = list(zip(perso, [200]*(end-begin)))
            obj = pyganim.PygAnimation(frames)
            obj.play()
        else:
            obj = perso[0]
        return obj

    def AddLifeBar(self, tile_size):
        width = 2
        percentage = self._cara['PV']/self._cara['PV_max']
        height_life = tile_size*percentage
        height_void = tile_size - height_life
        if percentage < 0.5:
            G = 255 - 255*(1-percentage*2)
            R = 255
        else:
            R = 255*(1-percentage)*2
            G = 255
        B = 0
        self._lifebar1 = Highlight.Highlight(height_life, width, 255, (R, G, B), self._pos[0], self._pos[1])
        self._lifebar2 = Highlight.Highlight(height_void, width, 255, (0, 0, 0), self._pos[0]+height_life, self._pos[1])

    def pos(self, tile_size, pos_pixel = None, pos_tile = None):
        if pos_pixel:
            self._pos = pos_pixel
            self._pos_tile = (pos_pixel[0]/tile_size, pos_pixel[1]/tile_size)
        elif pos_tile:
            self._pos_tile = pos_tile
            self._pos = (pos_tile[0]*tile_size, pos_tile[1]*tile_size)

    def PhysicalReduction(self, dmg, element):
        # Each defense point reduce the damages by 0.4%
        random = uniform(0.9, 1.1)
        reduction = 1-util.StatCalculation(self._cara['defense'])
        return int(random*dmg*reduction*(1-self._cara['elementalRes'][element]))

    def MagicalReduction(self, dmg, element):
        # Each resistance point reduce the damages by 0.4%
        random = uniform(0.9, 1.1)
        reduction = 1-util.StatCalculation(self._cara['resistance'])
        return int(random*dmg*reduction*(1-self._cara['elementalRes'][element]))

    def PhysicalDmg(self, dmg):
        random = uniform(0.9, 1.1)
        enhance = 1+util.StatCalculation(self._cara['strength'])
        return int(random*dmg*enhance)

    def MagicalDmg(self, dmg):
        random = uniform(0.9, 1.1)
        enhance = 1+util.StatCalculation(self._cara['magic'])
        return int(random*dmg*enhance)

    def Affect(self,effect, screen):
        xp = 0
        if type(effect) == int:
            xp = abs(self._xp_on_damage*effect)
            self._cara['PV'] = min(self._cara['PV_max'], max(0,self._cara['PV']-effect))
        else:# It's a debuff, a buff, or anything else
            self._cara['effects'].append(effect)
            self._cara[effect._properties] = max(0, self._cara[effect._properties]-effect._power)
        for i in self._index:
            screen.RemoveObject(i)
        if self._cara['PV'] == 0:
                self._dead = True
                xp += self._xp_on_kill
        else:
            self.AddLifeBar(screen._tile_size)
            self._index = screen.AddCharacter(self, 'standing')
        return xp

    def Attack(self, skill, tiles, screen):
        affected = []
        for character in screen._characters:
            if character._pos_tile in tiles:
                affected.append(character)
        self._xp += skill.Affect(self, affected, tiles, screen)
        self._cara['PA'] -= skill._cost

    def passTurn(self):
        self._cara['PA'] = self._cara['PA_max']
        self._cara['PM'] = self._cara['PM_max']
        for i, effect in enumerate(self._cara['effects']):
            if effect:
                if effect._duration == effect._since:
                    self._cara['effects'][i] = False
                elif effect._since == 0 and effect._properties not in ['PA', 'PM']:
                    self._cara['effects'][i]._since += 1
                else:
                    self._cara['effects'][i]._since += 1
                    self._cara[effect._properties] = max(0, self._cara[effect._properties]-effect._power)

    def IA_Action(self, screen):
        if self._ia == 'aggresif' or self._ia == 'defensif':
            reachable = self.getReachable(screen)
        elif self._ia == 'passif':
            reachable = {(self._pos_tile):(0, [])}
            pass
        max_dmgs = 0
        path, skill_target, tiles_target = False, False, False
        for skill in self._skills:
            for tile in reachable:
                targets = set(skill.GetAimable(tile, screen._map_data, screen._tile_size, self._team))
                for target in targets:
                    dmgs = 0
                    affected = []
                    final_tiles = skill.AOE(target, self, screen)
                    if tile in final_tiles:
                        affected.append(self)
                    for target_character in screen._characters:
                        if target_character._pos_tile in final_tiles and target_character != self:
                            affected.append(target_character)
                    for target_character in affected:
                            if skill._type == 'magic':
                                dmg = self.MagicalDmg(skill._damage)
                                dmg = target_character.MagicalReduction(dmg, skill._ele)
                            elif skill._type == 'physic':
                                dmg = self.PhysicalDmg(skill._damage)
                                dmg = target_character.PhysicalReduction(dmg, skill._ele)
                            if self._team == target_character._team:
                                dmgs -= 2*dmg
                            else:
                                dmgs += dmg
                    if max_dmgs < dmgs:
                        d, path = reachable[tile]
                        path.append(tile)
                        tiles_target = final_tiles
                        skill_target = skill
                        max_dmgs = dmgs
        if path:
            for tile in path[1:]:
                self.Move(screen, 0, self._pos_tile, tile)
            self._cara['PM'] -= d
        if skill_target and tiles_target:
            self.Attack(skill_target, tiles_target, screen)

    def Move(self, screen, p, ini_pos, new_pos):
        if ini_pos[0] > new_pos[0]:
            diff = (-screen._tile_size, 0)
        elif ini_pos[0] < new_pos[0]:
            diff = (screen._tile_size, 0)
        elif ini_pos[1] > new_pos[1]:
            diff = (0, -screen._tile_size)
        elif ini_pos[1] < new_pos[1]:
            diff = (0, screen._tile_size)
        else :
            return
        self._cara['PM'] -= p
        self._lifebar1._pos = (self._lifebar1._pos[0] + diff[0], self._lifebar1._pos[1] + diff[1])
        self._lifebar2._pos = (self._lifebar2._pos[0] + diff[0], self._lifebar2._pos[1] + diff[1])
        self.pos(screen._tile_size, pos_tile = new_pos)
        screen._objects[self._index[0]][1] = self._pos
        screen._objects[self._index[1]][1] = self._lifebar1._pos
        screen._objects[self._index[2]][1] = self._lifebar2._pos
        screen.MoveCircle(pos = self._pos)
        screen.UpdateStatus(self)


    def getReachable(self, screen):
        queue = {}
        queue[(self._pos_tile[0], self._pos_tile[1])] = (0, [])
        reachable = {}
        tile_size = screen._tile_size
        transparent = True
        while queue:
            x, y = list(queue.keys())[0]
            d, path = queue.pop((x, y))
            reachable[(x, y)] = (d, path)
            PM = self._cara['PM'] - d
            circle = (x-1, y), (x+1, y), (x, y-1), (x, y+1)
            for tile in circle:
                d_to = int(Map.CheckProperties((tile[0]*tile_size, tile[1]*tile_size), 'slowness', screen._map_data,tile_size))
                if tile[0] < 0 or tile[0] >= screen._width//tile_size:
                    transparent = False  # Outside of screen
                elif tile[1] < 0 or tile[1] >= screen._width//tile_size:
                    transparent = False # Outside of screen
                elif tile in reachable and d_to+d > reachable[(tile[0], tile[1])][0]:
                    transparent = False # Shorter path already in reachable
                for character in screen._characters:
                    if character._team != self._team:
                        transparent = False  # Obstacle on the path
                if transparent and d_to != -1 and  d+d_to <= PM:  # Obstacle on the path
                    queue[(tile[0], tile[1])] = (d+d_to, path+[(x, y)])
        return reachable


class Anna(Character):
    def __init__(self, tile_size, pos_tile, ia, save=None):
        Character.__init__(self, ia)
        self._id = 1
        self._cara['name'] = 'Anna'
        self._cara['sex'] = 'f'
        self._rows, self._cols = 144, 12
        self._sprite['standing'] = self.AddSprite(0,4)
        self._sprite['static'] = self.AddSprite(0)
        self._sprite['attacking'] =  self.AddSprite(12,16)
        self._sprite['walking_left'] =  self.AddSprite(24,28)
        self._sprite['walking_right'] =  self.AddSprite(36,40)
        self._sprite['walking_down'] =  self.AddSprite(48,52)
        self._sprite['walking_up'] =  self.AddSprite(50,56)
        self._portrait = pygame.image.load(join('res', 'sprite', 'Anna_portrait.png'))
        self.pos(tile_size, pos_tile = pos_tile)
        if save:
            pass
        else:
            skills = ['Execution', 'Horizontal', 'Vertical']
            self._skills = [Skill.Skill.Initialization(skill) for skill in skills]
            self._cara['PV'], self._cara['PV_max'] = 100, 100
            self._cara['PA'], self._cara['PA_max'] = 6, 6
            self._cara['PM'], self._cara['PM_max'] = 3, 3
            self._cara['speed'] = 50
        self.AddLifeBar(tile_size)

class Henry(Character):
    def __init__(self, tile_size, pos_tile, ia, save=None):
        Character.__init__(self, ia)
        self._sprite = {}
        self._id = 2
        self._cara['name'] = 'Henry'
        self._cara['sex'] = 'm'
        self._rows, self._cols = 80, 12
        self._sprite['standing'] = self.AddSprite(388,392)
        self._sprite['static'] = self.AddSprite(388)
        self._sprite['attacking'] =  self.AddSprite(400,404)
        self._sprite['walking_left'] =  self.AddSprite(412,416)
        self._sprite['walking_right'] =  self.AddSprite(424,428)
        self._sprite['walking_down'] =  self.AddSprite(436,440)
        self._sprite['walking_up'] =  self.AddSprite(448,452)
        self._portrait = pygame.image.load(join('res', 'sprite', 'Henry_portrait.png'))
        self.pos(tile_size, pos_tile = pos_tile)
        if save:
            pass
        else:
            skills = ['Apocalypse', 'Horizontal']
            self._skills = [Skill.Skill.Initialization(skill) for skill in skills]
            self._cara['PV'], self._cara['PV_max'] = 20, 100
            self._cara['PA'], self._cara['PA_max'] = 6, 6
            self._cara['PM'], self._cara['PM_max'] = 3, 3
            self._cara['speed'] = 80
        self.AddLifeBar(tile_size)