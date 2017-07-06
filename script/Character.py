from os.path import join
from . import Highlight, Skill, util, Map, TextBox
import sys
import json
from random import uniform
import pygame
from pygame.locals import *  # Import the event
import pyganim

class Character():
    def __init__(self, file,team = 0, tile_size = None, pos_tile = False, ia = False, leader = False, coef=1):
        self._index, self._lifebar = None, (None, None)
        self._ia, self._leader, self._team = ia, leader, team
        self._dead = False
        self._direction = 2
        self.FromJSON(file)
        if pos_tile:
            self.UpdatePos(tile_size, pos_tile = tuple(pos_tile))
        else:
            self._tile, self._px = None, None

        for key in self._cara['growth']:
            self._cara[key]*=coef
        self._cara['PV_max']*=coef


    def FromJSON(self, file):
        with open(join('res','json', 'character', file+'.json'), 'r') as file:
            data = json.load(file)['character']
        self._cara = data['cara']
        self._sprite = {'values': data['sprite']}
        self._sheet_name = data['sheet']
        self.CreateSprite()
        skills = [(Skill.Skill(skill[0]), skill[1]) for skill in data['skill']]
        self._skills = []
        self._next_skills = []
        for skill, level in skills:
            if level>0 and self._cara['level'] >= level:
                self._skills.append(skill)
            else:
                self._next_skills.append([skill, level])

    def ToJSON(self):
        """Write the character in a .json
        Input :
        self - a character

        Output :
        Nothing, but a .json est written"""
        skills = [skill._cara['name'] for skill in self._skills]
        temp = {'cara':self._cara, 'sprite':self._sprite['values'],
                'skill':skills, 'sheet':self._sheet_name}
        util.WriteJSON({'character':temp}, self._cara['name'])

    def CreateSprite(self):
        """From ._sprite['values'] get all sprites
        Input:
        self - a character

        Output:
        Nothing, but ._sprite is update"""
        for key, value in self._sprite['values'].items():
            if key in ['cols', 'rows']:
                continue
            if key == 'portrait':
                value = join('res','sprite', self._cara['name'], value)
                self._sprite[key] = pygame.image.load(value)
            elif len(value) == 2:
                self._sprite[key] = self.AddSprite(value[0], value[1])
            else:
                self._sprite[key] = self.AddSprite(value[0])


    def AddSprite(self, begin, end=False):
        """Make a sprite (animated or not) from a sheet

        Input:
        self - character
        begin - int
        end - int, false of the sprite isn't animated

        Output:
        obj - a sprite"""
        print('AddSpriteCharacter:', begin, end)
        rows = self._sprite['values']['rows']
        cols = self._sprite['values']['cols']
        if not end:
            end = begin+1
        fullname = join('res', 'sprite', self._cara['name'], str(self._sheet_name) + '.png')
        perso = pyganim.getImagesFromSpriteSheet(fullname,cols=cols,rows= rows)[begin:end]
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
        percentage = self._cara['PV']/self._cara['PV_max']
        height_life = tile_size*percentage
        size1 = (height_life,2)
        size2 = (tile_size - height_life,2)
        pos2 = (self._pixel[0]+height_life, self._pixel[1])
        if percentage < 0.5:
            G = 255 - 255*(1-percentage*2)
            R = 255
        else:
            R = 255*(1-percentage)*2
            G = 255
        B = 0
        l1 = Highlight.Highlight(size1, 255, (R, G, B), self._pixel)
        l2 = Highlight.Highlight(size2, 255, (0, 0, 0), pos2)
        self._lifebar = (l1, l2)

    def UpdatePos(self, tile_size, pos_pixel = None, pos_tile = None):
        """Update pos_pixel or pos_tile

        Input:
        self - character
        tile_size - int: number of pixel of the tile side
        pos_pixel - optional tuple of int
        pos_tile - optional tuple of int"""
        if pos_pixel:
            self._pixel = pos_pixel
            self._tile = (pos_pixel[0]/tile_size, pos_pixel[1]/tile_size)
        elif pos_tile:
            self._tile = pos_tile
            self._pixel = (pos_tile[0]*tile_size, pos_tile[1]*tile_size)
        else:
            self._pixel = None
            self._tile = None
            return
        self.AddLifeBar(tile_size)

    def PhysicalReduction(self, dmg, element):
        """return a int, lower than 1"""
        random = uniform(0.9, 1.1)
        reduction = util.StatCalculation(self._cara['defense'])
        return int(random*dmg*reduction*(util.StatCalculation(self._cara['elementalRes'][element])))

    def MagicalReduction(self, dmg, element):
        """return a int, lower than 1"""
        random = uniform(0.9, 1.1)
        reduction = util.StatCalculation(self._cara['resistance'])
        return int(random*dmg*reduction*(util.StatCalculation(self._cara['elementalRes'][element])))

    def PhysicalDmg(self, dmg):
        """return a int, higher than 1"""
        random = uniform(0.9, 1.1)
        enhance = util.StatCalculation(self._cara['strength'])
        return int(random*dmg/enhance)

    def MagicalDmg(self, dmg):
        """return a int, higher than 1"""
        random = uniform(0.9, 1.1)
        enhance = util.StatCalculation(self._cara['magic'])
        return int(random*dmg/enhance)

    def getCara(self, p):
        return util.StatCalculation(self._cara[p])

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
            xp = abs(self._cara['xp']['on_damage']*effect)
            self._cara['PV'] = min(self._cara['PV_max'], max(0,self._cara['PV']-effect))
        else:# It's a debuff, a buff, or anything else
            self._cara['effects'].append(effect)
            v = max(0, self._cara[effect._properties]-effect._power)
            self._cara[effect._properties] = v
        if self._cara['PV'] == 0:
            self._dead = True
            xp += self._cara['xp']['on_kill']
            for i in self._index:
                screen.RemoveObject(i)
        else:
            self.AddLifeBar(screen._tile_size)
            screen._objects[self._index[1]][0] = self._lifebar[0]._content
            screen._objects[self._index[2]][0] = self._lifebar[1]._content
        return xp

    def AddXP(self, xp, screen):
        self._cara['xp']['current'] += xp
        while self._cara['xp']['current'] > 100:
            self._cara['xp']['current'] = self._cara['xp']['current']-100
            self.LevelUp(screen)


    def LevelUp(self, screen):
        if self._team == 1:
            pos = (int((screen._size[0]-288)/2), int((screen._size[1]-174)/2))
            index = screen.AddTextBox(TextBox.LevelUp(self), pos)
            loop = True
            mainClock = pygame.time.Clock()
            while loop:
                screen.refresh()
                mainClock.tick(30)
                for event in pygame.event.get():
                    if event.type == QUIT:  # The game is closed
                        pygame.quit()
                        sys.exit()
                    if event.type == KEYDOWN:
                        loop = False
            for i in index:
                screen.RemoveObject(i)
        self._cara['level'] += 1
        self._cara['PV_max'] += self._cara['growth']['PV']
        self._cara['PV'] += self._cara['growth']['PV']
        self._cara['strength'] += self._cara['growth']['strength']
        self._cara['defense'] += self._cara['growth']['defense']
        self._cara['magic'] += self._cara['growth']['magic']
        self._cara['resistance'] += self._cara['growth']['resistance']
        self._cara['speed'] += self._cara['growth']['speed']
        for i, obj in enumerate(self._next_skills):
            skill, level = obj
            if level > 0 and self._cara['level'] >= level:
                self._skills.append(skill)
                self._next_skills[i][1] = -1
        return

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
        tile_type = Map.CheckProperties(self._tile, 'type',
                                        screen._map_data, screen._tile_size)
        if w:
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
            if character._tile in tiles:
                affected.append(character)

        self._cara = cara
        self.AddXP(skill.Affect(self, affected, tiles, screen), screen)
        self._cara['PA'] -= skill._cara['cost']
        direction = util.GetDirection(self._tile, tile_target)
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
                    v = max(0, self._cara[effect._properties]-effect._power)
                    self._cara[effect._properties] = v

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
            reachable = {(self._tile):(0, [])}
        max_dmgs = 0
        path, skill_target, tiles_target = False, False, False
        for skill in self._skills:
            for tile in reachable:
                targets = set(skill.GetAimable(tile, screen, self))
                for target in targets:
                    dmgs = 0
                    affected = []
                    final_tiles = skill.AOE(target, self, screen)
                    if tile in final_tiles:
                        affected.append(self)
                    for target_character in screen._characters:
                        if target_character._tile in final_tiles and target_character != self:
                            affected.append(target_character)
                    for target_character in affected:
                            if skill._cara['type'] == 'magic':
                                dmg = self.MagicalDmg(skill._cara['damage'])
                                dmg = target_character.MagicalReduction(dmg, skill._cara['ele'])
                            elif skill._cara['type'] == 'physic':
                                dmg = self.PhysicalDmg(skill._cara['damage'])
                                dmg = target_character.PhysicalReduction(dmg, skill._cara['ele'])
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
                self.Move(screen, 0, self._tile, tile)
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
        pix_pos = self._pixel
        ini_bar1 = self._lifebar[0]._pixel
        ini_bar2 = self._lifebar[1]._pixel
        screen._objects[self._index[0]][0] = animation
        screen._objects[self._index[0]][2] = 'character'
        n = screen._animation_length
        for i in range(n+1):
            temp_pos = int(diff[0]*i/n), int(diff[1]*i/n)
            full_temp_pos = pix_pos[0]+temp_pos[0], pix_pos[1]+temp_pos[1]
            self._lifebar[0]._pixel = (ini_bar1[0] + temp_pos[0], ini_bar1[1] + temp_pos[1])
            self._lifebar[1]._pixel = (ini_bar2[0] + temp_pos[0], ini_bar2[1] + temp_pos[1])
            self.UpdatePos(screen._tile_size, pos_pixel = full_temp_pos)
            screen._objects[self._index[0]][1] = self._pixel
            screen._objects[self._index[1]][1] = self._lifebar[0]._pixel
            screen._objects[self._index[2]][1] = self._lifebar[1]._pixel
            screen.MoveCircle(pos = self._pixel)
            screen.refresh()
        screen._objects[self._index[0]][0] = static
        screen._objects[self._index[0]][2] = 'sprite'
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
        queue[(self._tile[0], self._tile[1])] = (0, [])
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
                d_to = int(Map.CheckProperties((tile[0]*tile_size, tile[1]*tile_size),
                                               'slowness', screen._map_data,tile_size))
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
