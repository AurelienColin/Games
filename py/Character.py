from os.path import join
from . import Highlight, Skill, util, Map, TextBox, Item, Effect
import sys
import json
from random import uniform
import pygame
from pygame.locals import *  # Import the event
import pyganim

class Character():
    def __init__(self, file,team = 0, tileSize = None, posTile = False, ia = False, leader = False, coef=1):
        self.index, self.lifebar = None, (None, None)
        self.ia, self.leader, self.team = ia, leader, team
        self.dead = False
        self.direction = 2
        self.FromJSON(file)

        self.pos = {}
        if posTile:
            self.UpdatePos(tileSize, posTile = tuple(posTile))
        else:
            self.pos = {'tile':None, 'px':None}
        for key in self.cara['growth']:
            self.cara[key]*=coef
        self.cara['PV_max']*=coef


    def FromJSON(self, file):
        with open(join('res','json', 'character', file+'.json'), 'r') as file:
            data = json.load(file)['character']
        self.cara = data['cara']
        self.sprite = {'values': data['sprite']}
        self.sheetName = data['sheet']
        self.CreateSprite()
        self.items = {place:Item.Item(item[0]) for place, item in data['items'].items()}
        [self.Equip(name) for name, equiped in data['items'].values() if equiped]
        skills = [(Skill.Skill(skill), level) for skill, level in data['skill']]
        self.skills = []
        self.nextSkills = []
        for skill, level in skills:
            if level>0 and self.cara['level'] >= level:
                self.skills.append(skill)
            else:
                self.nextSkills.append([skill, level])

    def ToJSON(self):
        """Write the character in a .json
        Input :
        self - a character

        Output :
        Nothing, but a .json est written"""
        skills = [skill.cara['name'] for skill in self.skills]
        temp = {'cara':self.cara, 'sprite':self.sprite['values'],
                'skill':skills, 'sheet':self.sheetName, 'items':self.items}
        util.WriteJSON({'character':temp}, self.cara['name'])

    def Equip(self, name):
        item = self.getItem(name)
        for cara, power in item.cara.items():
            self.cara[cara]+=power
        item.equiped=True

    def Desequip(self, name):
        item = self.getItem(name)
        for cara, power in item.cara.items():
            self.cara[cara]-=power
        item.equiped=False

    def UseItem(self, name, screen):
        item = self.getItem(name)
        for cara, value in item.use.items():
            power, length = value
            effect = Effect.Effect(cara, power, length)
            self.Affect(effect, screen)
            self.cara['effects'].append(effect)
        self.cara['PA']-=item.cost
        item.ReduceDurability()

    def getItem(self, name):
        print(name, [item.name for item in self.items.values()])
        for item in self.items.values():
            if item.name == name:
                return item

    def CreateSprite(self):
        """From .sprite['values'] get all sprites
        Input:
        self - a character

        Output:
        Nothing, but .sprite is update"""
        for key, value in self.sprite['values'].items():
            if key in ['cols', 'rows']:
                continue
            if key == 'portrait':
                value = join('res','sprite', self.cara['name'], value)
                self.sprite[key] = pygame.image.load(value)
            elif len(value) == 2:
                self.sprite[key] = self.AddSprite(value[0], value[1])
            else:
                self.sprite[key] = self.AddSprite(value[0])

    def AddSprite(self, begin, end=False):
        """Make a sprite (animated or not) from a sheet

        Input:
        self - character
        begin - int
        end - int, false of the sprite isn't animated

        Output:
        obj - a sprite"""
        print('AddSpriteCharacter:', begin, end)
        rows = self.sprite['values']['rows']
        cols = self.sprite['values']['cols']
        if not end:
            end = begin+1
        fullname = join('res', 'sprite', self.cara['name'], str(self.sheetName) + '.png')
        perso = pyganim.getImagesFromSpriteSheet(fullname,cols=cols,rows= rows)[begin:end]
        if end > begin+1:
            frames = list(zip(perso, [200]*(end-begin)))
            obj = pyganim.PygAnimation(frames)
            obj.play()
        else:
            obj = perso[0]
        return obj

    def AddLifeBar(self, tileSize):
        """Add lifes bar (one black for the lost PV, one colored for the remaining one

        Input:
        self - character
        tileSize - int: number of pixel of the tile side
        """
        percentage = min(1,max(0,self.cara['PV']/self.cara['PV_max']))
        height_life = tileSize*percentage
        size1 = (height_life,2)
        size2 = (tileSize - height_life,2)
        pos2 = (self.pos['px'][0]+height_life, self.pos['px'][1])
        if percentage < 0.5:
            G = 255 - 255*(1-percentage*2)
            R = 255
        else:
            R = 255*(1-percentage)*2
            G = 255
        B = 0
        l1 = Highlight.Highlight(size1, 255, (R, G, B), self.pos['px'])
        l2 = Highlight.Highlight(size2, 255, (0, 0, 0), pos2)
        self.lifebar = (l1, l2)

    def UpdatePos(self, tileSize, posPixel = None, posTile = None):
        """Update posPixel or pos_tile

        Input:
        self - character
        tileSize - int: number of pixel of the tile side
        posPixel - optional tuple of int
        pos_tile - optional tuple of int"""
        if posPixel:
            self.pos['px'] = posPixel
            self.pos['tile'] = (posPixel[0]/tileSize, posPixel[1]/tileSize)
        elif posTile:
            self.pos['tile'] = posTile
            self.pos['px'] = (posTile[0]*tileSize, posTile[1]*tileSize)
        else:
            self.pos['px'] = None
            self.pos['tile'] = None
            return
        self.AddLifeBar(tileSize)

    def PhysicalReduction(self, dmg, element):
        """return a int, lower than 1"""
        random = uniform(0.9, 1.1)
        reduction = util.StatCalculation(self.cara['defense'])
        return int(random*dmg*reduction*(util.StatCalculation(self.cara['elementalRes'][element])))

    def MagicalReduction(self, dmg, element):
        """return a int, lower than 1"""
        random = uniform(0.9, 1.1)
        reduction = util.StatCalculation(self.cara['resistance'])
        return int(random*dmg*reduction*(util.StatCalculation(self.cara['elementalRes'][element])))

    def PhysicalDmg(self, dmg):
        """return a int, higher than 1"""
        random = uniform(0.9, 1.1)
        enhance = util.StatCalculation(self.cara['strength'])
        return int(random*dmg/enhance)

    def MagicalDmg(self, dmg):
        """return a int, higher than 1"""
        random = uniform(0.9, 1.1)
        enhance = util.StatCalculation(self.cara['magic'])
        return int(random*dmg/enhance)

    def getCara(self, p):
        return util.StatCalculation(self.cara[p])

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
            xp = abs(self.cara['xp']['on_damage']*effect)
            self.cara['PV'] = min(self.cara['PV_max'], max(0,self.cara['PV']-effect))
        else:# It's a debuff, a buff, or anything else
            self.cara['effects'].append(effect)
            v = max(0, self.cara[effect.properties]+effect.power)
            self.cara[effect.properties] = v
        if self.cara['PV'] == 0:
            self.dead = True
            xp += self.cara['xp']['on_kill']
            for i in self.index:
                screen.RemoveObject(i)
        else:
            self.AddLifeBar(screen.tileSize)
            screen.objects[self.index[1]][0] = self.lifebar[0].content
            screen.objects[self.index[2]][0] = self.lifebar[1].content
        return xp

    def AddXP(self, xp, screen):
        self.cara['xp']['current'] += xp
        while self.cara['xp']['current'] > 100:
            self.cara['xp']['current'] = self.cara['xp']['current']-100
            self.LevelUp(screen)


    def LevelUp(self, screen):
        if self.team == 1:
            pos = (int((screen.size[0]-288)/2), int((screen.size[1]-174)/2))
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
        self.cara['level'] += 1
        self.cara['PV_max'] += self.cara['growth']['PV']
        self.cara['PV'] += self.cara['growth']['PV']
        self.cara['strength'] += self.cara['growth']['strength']
        self.cara['defense'] += self.cara['growth']['defense']
        self.cara['magic'] += self.cara['growth']['magic']
        self.cara['resistance'] += self.cara['growth']['resistance']
        self.cara['speed'] += self.cara['growth']['speed']
        for i, obj in enumerate(self.nextSkills):
            skill, level = obj
            if level > 0 and self.cara['level'] >= level:
                self.skills.append(skill)
                self.nextSkills[i][1] = -1
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
        cara = self.cara
        w, s = util.WeakAgainst(cara['type'])
        tile_type = Map.CheckProperties(self.pos['tile'], 'type',
                                        screen.mapData, screen.tileSize)
        if w:
            if tile_type == w:
                affected.cara['magic'] -= 56
                affected.cara['strength'] -= 56
                affected.cara['speed'] -= 56
                affected.cara['hit'] -= 56
            elif tile_type == cara['type']:
                affected.cara['magic'] += 56
                affected.cara['strength'] += 56
                affected.cara['speed'] += 56
                affected.cara['hit'] += 56
        for character in screen.characters:
            if character.pos['tile'] in tiles:
                affected.append(character)

        self.cara = cara
        self.AddXP(skill.Affect(self, affected, tiles, screen), screen)
        self.cara['PA'] -= skill.cara['cost']
        direction = util.GetDirection(self.pos['tile'], tile_target)
        if direction == 0:
            static = self.sprite['static_up']
        elif direction == 1:
            static = self.sprite['static_left']
        elif direction == 2:
            static = self.sprite['static_down']
        elif direction == 3:
            static = self.sprite['static_right']
        self.direction = direction
        screen.objects[self.index[0]][0] = static
        screen.objects[self.index[0]][2] = 'sprite'


    def passTurn(self):
        """Finish the turn of the character

        Input:
        self - character

        Output:
        PA, PM, and effect are updated"""
        self.cara['PA'] = self.cara['PA_max']
        self.cara['PM'] = self.cara['PM_max']
        for i, effect in enumerate(self.cara['effects']):
            if effect:
                if effect.duration == effect.since:
                    self.cara['effects'][i] = False
                elif effect.since == 0 and effect.properties not in ['PA', 'PM']:
                    self.cara['effects'][i].since += 1
                else:
                    self.cara['effects'][i].since += 1
                    v = max(0, self.cara[effect.properties]-effect.power)
                    self.cara[effect.properties] = v

    def IA_Action(self, screen):
        """Execute the ia

        Onput:
        self - character
        screen - screen

        Output:
        character move and attack, screen and character are updated
        """
        if self.ia == 'aggresif' or self.ia == 'defensif':
            reachable = self.getReachable(screen)
        elif self.ia == 'passif':
            reachable = {(self.pos['tile']):(0, [])}
        max_dmgs = 0
        path, skill_target, tiles_target = False, False, False
        for skill in self.skills:
            for tile in reachable:
                targets = set(skill.GetAimable(tile, screen, self))
                for target in targets:
                    dmgs = 0
                    affected = []
                    finalTiles = skill.AOE(target, self, screen)
                    if tile in finalTiles:
                        affected.append(self)
                    for targetchar in screen.characters:
                        if targetchar.pos['tile'] in finalTiles and targetchar != self:
                            affected.append(targetchar)
                    for targetchar in affected:
                            if skill.cara['type'] == 'magic':
                                dmg = self.MagicalDmg(skill.cara['damage'])
                                dmg = targetchar.MagicalReduction(dmg, skill.cara['ele'])
                            elif skill.cara['type'] == 'physic':
                                dmg = self.PhysicalDmg(skill.cara['damage'])
                                dmg = targetchar.PhysicalReduction(dmg, skill.cara['ele'])
                            if self.team == targetchar.team:
                                dmgs -= 2*dmg
                            else:
                                dmgs += dmg
                    if max_dmgs < dmgs:
                        d, path = reachable[tile]
                        path.append(tile)
                        tile_target = target
                        tiles_target = finalTiles
                        skill_target = skill
                        max_dmgs = dmgs
        if path:
            for tile in path[1:]:
                self.Move(screen, 0, self.pos['tile'], tile)
            self.cara['PM'] -= d
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
            diff = (-screen.tileSize, 0)
            animation = self.sprite['walking_left']
            static = self.sprite['static_left']
            self.direction = 1
        elif ini_pos[0] < new_pos[0]:
            diff = (screen.tileSize, 0)
            animation = self.sprite['walking_right']
            static = self.sprite['static_right']
            self.direction = 3
        elif ini_pos[1] > new_pos[1]:
            diff = (0, -screen.tileSize)
            animation = self.sprite['walking_up']
            static = self.sprite['static_up']
            self.direction = 0
        elif ini_pos[1] < new_pos[1]:
            diff = (0, screen.tileSize)
            animation = self.sprite['walking_down']
            static = self.sprite['static_down']
            self.direction = 2
        else :
            return
        self.cara['PM'] -= p
        pix_pos = self.pos['px']
        ini_bar1 = self.lifebar[0].pixel
        ini_bar2 = self.lifebar[1].pixel
        screen.objects[self.index[0]][0] = animation
        screen.objects[self.index[0]][2] = 'character'
        n = screen.frameNumber
        for i in range(n+1):
            temp_pos = int(diff[0]*i/n), int(diff[1]*i/n)
            full_temp_pos = pix_pos[0]+temp_pos[0], pix_pos[1]+temp_pos[1]
            self.lifebar[0].pixel = (ini_bar1[0] + temp_pos[0], ini_bar1[1] + temp_pos[1])
            self.lifebar[1].pixel = (ini_bar2[0] + temp_pos[0], ini_bar2[1] + temp_pos[1])
            self.UpdatePos(screen.tileSize, posPixel = full_temp_pos)
            screen.objects[self.index[0]][1] = self.pos['px']
            screen.objects[self.index[1]][1] = self.lifebar[0].pixel
            screen.objects[self.index[2]][1] = self.lifebar[1].pixel
            screen.MoveCircle(pos = self.pos['px'])
            screen.refresh()
        screen.objects[self.index[0]][0] = static
        screen.objects[self.index[0]][2] = 'sprite'
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
        queue[(self.pos['tile'][0], self.pos['tile'][1])] = (0, [])
        reachable = {}
        tileSize = screen.tileSize
        transparent = True
        while queue:
            x, y = list(queue.keys())[0]
            d, path = queue.pop((x, y))
            reachable[(x, y)] = (d, path)
            PM = self.cara['PM'] - d
            circle = (x-1, y), (x+1, y), (x, y-1), (x, y+1)
            for tile in circle:
                d_to = int(Map.CheckProperties((tile[0]*tileSize, tile[1]*tileSize),
                                               'slowness', screen.mapData,tileSize))
                if tile[0] < 0 or tile[0] >= screen.size[1]//tileSize:
                    transparent = False  # Outside of screen
                elif tile[1] < 0 or tile[1] >= screen.size[1]//tileSize:
                    transparent = False # Outside of screen
                elif tile in reachable and d_to+d > reachable[(tile[0], tile[1])][0]:
                    transparent = False # Shorter path already in reachable
                for character in screen.characters:
                    if character.team != self.team:
                        transparent = False  # Obstacle on the path
                if transparent and d_to != -1 and  d+d_to <= PM:  # Obstacle on the path
                    queue[(tile[0], tile[1])] = (d+d_to, path+[(x, y)])
        return reachable
