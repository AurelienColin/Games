import pyganim
from os.path import join
import Highlight

class Character():
    def __init__(self):
        self._sprite = {}
        self._cara = {}
        self._index = None
        self._lifebar1 = None
        self._lifebar2 = None
        self._pos = None

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
            self._skills = ['Exécution', 'Horizontal', 'Vertical']
            self._cara['PV'], self._cara['PV_max'] = 100, 100
            self._cara['PA'], self._cara['PA_max'] = 6, 6
            self._cara['PM'], self._cara['PM_max'] = 3, 3
            self._cara['speed'] = 100
            self._cara['attack'] = 100
            self._cara['defense'] = 100
            self._cara['effects'] = []

class Henry(Character):
    def __init__(self, save=None):
        Character.__init__(self)
        self._cara = {}
        self._sprite = {}
        self._id = 2
        self._cara['name'] = 'Henry'
        self._cara['sex'] = 'm'
        self._rows, self._cols = 80, 12
        self._sprite['standing'] = self.AddSprite(0,4)
        self._sprite['attacking'] =  self.AddSprite(12,16)
        self._sprite['walking_left'] =  self.AddSprite(24,28)
        self._sprite['walking_right'] =  self.AddSprite(36,40)
        self._sprite['walking_down'] =  self.AddSprite(48,52)
        self._sprite['walking_up'] =  self.AddSprite(50,56)
        if save:
            pass
        else:
            self._skills = ['Apocalypse']
            self._cara['PV'], self._cara['PV_max'] = 100, 100
            self._cara['PA'], self._cara['PA_max'] = 6, 6
            self._cara['PM'], self._cara['PM_max'] = 3, 3
            self._cara['speed'] = 100
            self._cara['attack'] = 100
            self._cara['defense'] = 100
            self._cara['effects'] = []
