import pyganim
from os.path import join
import Highlight
import Skill
import pygame
import util
import Map

from random import uniform

class Character():
    def __init__(self):
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
        self._team = 0
        self._direction = 2

        self._skills = []
        self._cara['PV'], self._cara['PV_max'] = 0, 0
        self._cara['PA'], self._cara['PA_max'] = 0, 0
        self._cara['PM'], self._cara['PM_max'] = 0, 0
        self._cara['type'] = 'neutral'
        self._cara['speed'] = 1
        self._cara['magic'] = 1
        self._cara['strength'] = 1
        self._cara['defense'] = 1
        self._cara['resistance'] = 1
        self._cara['hit'] = 1
        self._cara['avoid'] = 1
        self._cara['object'] = 1
        self._cara['effects'] = [False]
        self._cara['elementalRes'] = {'fire':1, 'water':1, 'earth':1,
                                      'wind':1, 'holy':1, 'unholy':1,
                                      'neutral':1}


    def Initialization(name, team, tile_size = None, pos_tile = False, ia = False, leader = False):
        """
        Input:
        name - string: name of the character
        team - int: 1 for the player, 2 for opponent
        tile_size - optional int
        pos_tile - optional tuple of int
        ia - optional string: False if the character is controlled by the player
        leader - optional boolean

        Output:
        self - character
        """
        if name == 'Anna':
            self = Anna()
        elif name == 'Henry':
            self = Henry()
        self._ia = ia
        self._leader = leader
        self._team = team
        if pos_tile:
            self.pos(tile_size, pos_tile = pos_tile)
        return self

    def AddSprite(self, begin, end=False):
        """Make a sprite (animated or not) from a sheet

        Input:
        self - character
        begin - int
        end - int, false of the sprite isn't animated

        Output:
        obj - a sprite"""
        if not end:
            end = begin+1
        fullname = join('res', 'sprite', self._cara['name'], str(self._sheet_name) + '.png')
        perso = pyganim.getImagesFromSpriteSheet(fullname,cols=self._cols,rows= self._rows)[begin:end]
        if end > begin+1:
            frames = list(zip(perso, [200]*(end-begin)))
            obj = pyganim.PygAnimation(frames)
            obj.play()
        else:
            obj = perso[0]
        return obj

    def AddLifeBar(self, tile_size):
        """Add lifes bar (one black for the lost PV, one colored for the remaining one

        Input:
        self - character
        tile_size - int: number of pixel of the tile side
        """
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
        """Update pos_pixel or pos_tile

        Input:
        self - character
        tile_size - int: number of pixel of the tile side
        pos_pixel - optional tuple of int
        pos_tile - optional tuple of int"""
        if pos_pixel:
            self._pos = pos_pixel
            self._pos_tile = (pos_pixel[0]/tile_size, pos_pixel[1]/tile_size)
        elif pos_tile:
            self._pos_tile = pos_tile
            self._pos = (pos_tile[0]*tile_size, pos_tile[1]*tile_size)
        else:
            self._pos = None
            self._pos_tile = None
            return
        self.AddLifeBar(tile_size)

    def PhysicalReduction(self, dmg, element):
        """return a int, lower than 1"""
        random = uniform(0.9, 1.1)
        reduction = 1-util.StatCalculation(self._cara['defense'])
        return int(random*dmg*reduction*(1-util.StatCalculation(self._cara['elementalRes'][element])))

    def MagicalReduction(self, dmg, element):
        """return a int, lower than 1"""
        random = uniform(0.9, 1.1)
        reduction = 1-util.StatCalculation(self._cara['resistance'])
        return int(random*dmg*reduction*(1-util.StatCalculation(self._cara['elementalRes'][element])))

    def PhysicalDmg(self, dmg):
        """return a int, higher than 1"""
        random = uniform(0.9, 1.1)
        enhance = 1+util.StatCalculation(self._cara['strength'])
        return int(random*dmg*enhance)

    def MagicalDmg(self, dmg):
        """return a int, higher than 1"""
        random = uniform(0.9, 1.1)
        enhance = 1+util.StatCalculation(self._cara['magic'])
        return int(random*dmg*enhance)

    def Avoid(self):
        """result high => probability to hit high"""
        return 1+util.StatCalculation(self._cara['avoid'])

    def Hit(self):
        """result high => probability to hit low"""
        return 1+util.StatCalculation(self._cara['hit'])

    def Affect(self,effect, screen):
        """Return the xp resulting of the attack

        Input:
        self - character
        effect - effect, could be debuff, buff, heal or dmg
        screen - screen

        Output:
        xp - int: xp to add to the attacking character"""
        xp = 0
        if type(effect) == int:
            xp = abs(self._xp_on_damage*effect)
            self._cara['PV'] = min(self._cara['PV_max'], max(0,self._cara['PV']-effect))
        else:# It's a debuff, a buff, or anything else
            self._cara['effects'].append(effect)
            self._cara[effect._properties] = max(0, self._cara[effect._properties]-effect._power)
        if self._cara['PV'] == 0:
            self._dead = True
            xp += self._xp_on_kill
            for i in self._index:
                screen.RemoveObject(i)
        else:
            self.AddLifeBar(screen._tile_size)
            screen._objects[self._index[1]][0] = self._lifebar1._content
            screen._objects[self._index[2]][0] = self._lifebar2._content
        return xp

    def Attack(self, skill, tiles, screen, tile_target):
        """Use an attack
        Input:
        self - character
        skill - skill
        tiles - list of tuple of two int, all the tiles affected
        screen - screen
        tile_target - tuple of two int, original target of the skill

        Output
        PA, xp, position are updated
        skill is used"""
        affected = []
        cara = self._cara
        w, s = util.WeakAgainst(cara['type'])
        tile_type = Map.CheckProperties(self._pos_tile, 'type',
                                        screen._map_data, screen._tile_size)
        if tile_type == w:
            affected._cara['magic'] -= 56
            affected._cara['strength'] -= 56
            affected._cara['speed'] -= 56
            affected._cara['hit'] -= 56
        elif tile_type == cara['type']:
            affected._cara['magic'] += 56
            affected._cara['strength'] += 56
            affected._cara['speed'] += 56
            affected._cara['hit'] += 56
        for character in screen._characters:
            if character._pos_tile in tiles:
                affected.append(character)

        self._cara = cara
        self._xp += skill.Affect(self, affected, tiles, screen)
        self._cara['PA'] -= skill._cost
        direction = util.GetDirection(self._pos_tile, tile_target)
        if direction == 0:
            static = self._sprite['static_up']
        elif direction == 1:
            static = self._sprite['static_left']
        elif direction == 2:
            static = self._sprite['static_down']
        elif direction == 3:
            static = self._sprite['static_right']
        self._direction = direction
        screen._objects[self._index[0]][0] = static
        screen._objects[self._index[0]][2] = 'sprite'


    def passTurn(self):
        """Finish the turn of the character

        Input:
        self - character

        Output:
        PA, PM, and effect are updated"""
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
        """Execute the ia

        Onput:
        self - character
        screen - screen

        Output:
        character move and attack, screen and character are updated
        """
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
                        tile_target = target
                        tiles_target = final_tiles
                        skill_target = skill
                        max_dmgs = dmgs
        if path:
            for tile in path[1:]:
                self.Move(screen, 0, self._pos_tile, tile)
            self._cara['PM'] -= d
        if skill_target and tiles_target:
            self.Attack(skill_target, tiles_target, screen, tile_target)

    def Move(self, screen, p, ini_pos, new_pos):
        """Change the position of the character

        Input:
        self - character
        screen - screen
        p - int: cost of PM to go on the tile
        ini_pos - tuple of two int: position of the initial tile
        new_pos - tuple of two int: position of the final tile

        Output:
        character and screen are update"""
        if ini_pos[0] > new_pos[0]:
            diff = (-screen._tile_size, 0)
            animation = self._sprite['walking_left']
            static = self._sprite['static_left']
            self._direction = 1
        elif ini_pos[0] < new_pos[0]:
            diff = (screen._tile_size, 0)
            animation = self._sprite['walking_right']
            static = self._sprite['static_right']
            self._direction = 3
        elif ini_pos[1] > new_pos[1]:
            diff = (0, -screen._tile_size)
            animation = self._sprite['walking_up']
            static = self._sprite['static_up']
            self._direction = 0
        elif ini_pos[1] < new_pos[1]:
            diff = (0, screen._tile_size)
            animation = self._sprite['walking_down']
            static = self._sprite['static_down']
            self._direction = 2
        else :
            return
        self._cara['PM'] -= p
        pix_pos = self._pos
        ini_bar1 = self._lifebar1._pos
        ini_bar2 = self._lifebar2._pos
        screen._objects[self._index[0]][0] = animation
        screen._objects[self._index[0]][2] = 'character'
        n = screen._animation_length
        for i in range(n+1):
            temp_pos = int(diff[0]*i/n), int(diff[1]*i/n)
            full_temp_pos = pix_pos[0]+temp_pos[0], pix_pos[1]+temp_pos[1]
            self._lifebar1._pos = (ini_bar1[0] + temp_pos[0], ini_bar1[1] + temp_pos[1])
            self._lifebar2._pos = (ini_bar2[0] + temp_pos[0], ini_bar2[1] + temp_pos[1])
            self.pos(screen._tile_size, pos_pixel = full_temp_pos)
            screen._objects[self._index[0]][1] = self._pos
            screen._objects[self._index[1]][1] = self._lifebar1._pos
            screen._objects[self._index[2]][1] = self._lifebar2._pos
            screen.MoveCircle(pos = self._pos)
            screen.refresh()
        screen._objects[self._index[0]][0] = static
        screen._objects[self._index[0]][2] = 'sprite'
        print('final pos:', self._pos, self._pos[0]/screen._tile_size, self._pos[1]/screen._tile_size)
        screen.UpdateStatus(self)


    def getReachable(self, screen):
        """Return the tile reachable with current number of PM
        Input:
        self - character
        screen - screen

        Output:
        reachable -- A dict, [(xy)] = (d, path)
            xy -- tuple of two int : the position of tile
            d -- int, number of PM used to go from current to xy
            path -- list of tuple of two int : path to take from current to xy
        """
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
    def __init__(self, save=None):
        Character.__init__(self)
        self._id = 1
        self._sheet_name = 'Anna_sheet'
        self._cara['name'] = 'Anna'
        self._cara['sex'] = 'f'
        self._rows, self._cols = 144, 12
        self._sprite['standing'] = self.AddSprite(0,4)
        self._sprite['static'] = self.AddSprite(0)
        self._sprite['attacking'] =  self.AddSprite(12,16)
        self._sprite['walking_left'] =  self.AddSprite(24,28)
        self._sprite['static_left'] = self.AddSprite(24)
        self._sprite['walking_right'] =  self.AddSprite(36,40)
        self._sprite['static_right'] = self.AddSprite(36)
        self._sprite['walking_down'] =  self.AddSprite(48,52)
        self._sprite['static_down'] = self.AddSprite(48)
        self._sprite['walking_up'] =  self.AddSprite(60,64)
        self._sprite['static_up'] = self.AddSprite(60)
        self._portrait = pygame.image.load(join('res', 'sprite', self._cara['name'], 'Anna_portrait.png'))
        if save:
            pass
        else:
            skills = ['Execution', 'Horizontal', 'Vertical']
            self._skills = [Skill.Skill.Initialization(skill) for skill in skills]
            self._cara['PV'], self._cara['PV_max'] = 100, 100
            self._cara['PA'], self._cara['PA_max'] = 100, 100
            self._cara['PM'], self._cara['PM_max'] = 100, 100
            self._cara['speed'] = 50

class Henry(Character):
    def __init__(self, save=None):
        Character.__init__(self)
        self._sprite = {}
        self._id = 2
        self._sheet_name = 'Henry_sheet'
        self._cara['name'] = 'Henry'
        self._cara['sex'] = 'm'
        self._rows, self._cols = 80, 12
        self._sprite['standing'] = self.AddSprite(388,392)
        self._sprite['static'] = self.AddSprite(388)
        self._sprite['attacking'] =  self.AddSprite(400,404)
        self._sprite['walking_left'] =  self.AddSprite(412,416)
        self._sprite['static_left'] =  self.AddSprite(412)
        self._sprite['walking_right'] =  self.AddSprite(424,428)
        self._sprite['static_right'] =  self.AddSprite(424)
        self._sprite['walking_down'] =  self.AddSprite(436,440)
        self._sprite['static_down'] =  self.AddSprite(436)
        self._sprite['walking_up'] =  self.AddSprite(448,452)
        self._sprite['static_up'] =  self.AddSprite(448)
        self._portrait = pygame.image.load(join('res', 'sprite', self._cara['name'], 'Henry_portrait.png'))
        if save:
            pass
        else:
            skills = ['Apocalypse', 'Horizontal']
            self._skills = [Skill.Skill.Initialization(skill) for skill in skills]
            self._cara['PV'], self._cara['PV_max'] = 100, 100
            self._cara['PA'], self._cara['PA_max'] = 100, 100
            self._cara['PM'], self._cara['PM_max'] = 100, 100
            self._cara['speed'] = 80