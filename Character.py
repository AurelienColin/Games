import pyganim
from os.path import join
import Highlight
import Skill

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

        self._skills = []
        self._cara['PV'], self._cara['PV_max'] = 0, 0
        self._cara['PA'], self._cara['PA_max'] = 0, 0
        self._cara['PM'], self._cara['PM_max'] = 0, 0
        self._cara['speed'] = 0
        self._cara['magic'] = 0
        self._cara['strength'] = 0
        self._cara['defense'] = 0
        self._cara['resistance'] = 0
        self._cara['effects'] = []
        self._cara['elementalRes'] = {'fire':0, 'water':0, 'earth':0,
                                      'wind':0, 'holy':0, 'unholy':0,
                                      'neutral':0}


    def Initialization(name):
        if name == 'Anna':
            self = Anna()
        elif name == 'Henry':
            self = Henry()
        else:
            self = None
        return self

    def AddSprite(self, begin, end):
        fullname = join('res', 'sprite', str(self._id) + '.png')
        perso = pyganim.getImagesFromSpriteSheet(fullname,cols=self._cols,rows= self._rows)[begin:end]
        frames = list(zip(perso, [200]*(end-begin)))
        animObj = pyganim.PygAnimation(frames)
        animObj.play()
        return animObj

    def AddLifeBar(self, tile_size):
        width = 2
        percentage = self._cara['PV']/self._cara['PV_max']
        height_life = tile_size*percentage
        height_void = tile_size - height_life
        if percentage < 0.5:
            G = 255 - 255*(1-percentage*2)
        else:
            R = 255
            R = 255*(1-percentage)*2
            G = 255
        B = 0
        print(R,G,B)
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
        reduction = pow(0.996, self._cara['defense'])
        return int(random*dmg*reduction*(1+self._cara['elementalRes'][element]))

    def MagicalReduction(self, dmg, element):
        # Each resistance point reduce the damages by 0.4%
        random = uniform(0.9, 1.1)
        reduction = pow(0.996, self._cara['resistance'])
        return int(random*dmg*reduction*(1+self._cara['elementalRes'][element]))

    def PhysicalDmg(self, dmg):
        random = uniform(0.9, 1.1)
        return int(random*dmg*pow(0.996, self._cara['strength']))

    def MagicalDmg(self, dmg):
        random = uniform(0.9, 1.1)
        return int(random*dmg*pow(0.996, self._cara['magic']))

    def Affect(self,effect):
        if type(effect) == int:
            pass  # It is a damage if positif, heal if negatif
        else:
            pass  # It's a debuff, a buff, or anything else

class Anna(Character):
    def __init__(self, save=None):
        Character.__init__(self)
        self._id = 1
        self._cara['name'] = 'Anna'
        self._cara['sex'] = 'f'
        self._rows, self._cols = 144, 12
        self._sprite['standing'] = self.AddSprite(0,4)
        self._sprite['attacking'] =  self.AddSprite(12,16)
        self._sprite['walking_left'] =  self.AddSprite(24,28)
        self._sprite['walking_right'] =  self.AddSprite(36,40)
        self._sprite['walking_down'] =  self.AddSprite(48,52)
        self._sprite['walking_up'] =  self.AddSprite(50,56)
        if save:
            pass
        else:
            skills = ['Execution', 'Horizontal', 'Vertical']
            self._skills = [Skill.Skill.Initialization(skill) for skill in skills]
            self._cara['PV'], self._cara['PV_max'] = 100, 100
            self._cara['PA'], self._cara['PA_max'] = 6, 6
            self._cara['PM'], self._cara['PM_max'] = 3, 3

class Henry(Character):
    def __init__(self, save=None):
        Character.__init__(self)
        self._sprite = {}
        self._id = 2
        self._cara['name'] = 'Henry'
        self._cara['sex'] = 'm'
        self._rows, self._cols = 80, 12
        self._sprite['standing'] = self.AddSprite(388,392)
        self._sprite['attacking'] =  self.AddSprite(400,404)
        self._sprite['walking_left'] =  self.AddSprite(412,416)
        self._sprite['walking_right'] =  self.AddSprite(424,428)
        self._sprite['walking_down'] =  self.AddSprite(436,440)
        self._sprite['walking_up'] =  self.AddSprite(448,452)
        if save:
            pass
        else:
            skills = ['Apocalypse']
            self._skills = [Skill.Skill.Initialization(skill) for skill in skills]
            self._cara['PV'], self._cara['PV_max'] = 100, 100
            self._cara['PA'], self._cara['PA_max'] = 6, 6
            self._cara['PM'], self._cara['PM_max'] = 3, 3
