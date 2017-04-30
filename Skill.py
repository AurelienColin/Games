import Highlight
import Screen

class Skill():
    def __init__(self):
        self._effects = {}
        pass

    def Initialization(name):
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
        center = (int(character._pos[0]/screen._tile_size),
                  int(character._pos[1]/screen._tile_size))
        aimable = GetAimable(center, self._range)
        highlighted = Highlight.HighlightTiles(screen._tile_size, aimable,
                                               60, (0, 0,255))
        blue = {}
        for pos in highlighted:
            blue[pos] = screen.AddHighlight(highlighted[pos])
        return blue

def GetAimable(pos, scope):
    aimable = set()
    for x in range(pos[0]-scope, pos[0]+scope+1):
        diff_x = abs(pos[0]-x)
        for y in range(pos[1]-scope, pos[1]+scope+1):
            diff_y = abs(pos[1]-y)
            if diff_x + diff_y <= scope:
                aimable.add((x, y))
    return aimable


class Horizontal(Skill):
    def __init__(self):
        Skill.__init__(self)
        self._name = 'Horizontal'
        self._AOE = 'parallel'
        self._size = 3
        self._cost = 4
        self._damage = 10
        self._range = 1
        self._sprite_sheet = None

class Vertical(Skill):
    def __init__(self):
        Skill.__init__(self)
        self._name = 'Vertical'
        self._AOE = 'orthogonal'
        self._size = 3
        self._cost = 4
        self._damage = 20
        self._range = 2
        self._sprite_sheet = None

class Execution(Skill):
    def __init__(self):
        Skill.__init__(self)
        self._name = 'Execution'
        self._AOE = None
        self._size = 3
        self._cost = 3
        self._damage = 30
        self._range = 1
        self._sprite_sheet = None

class Apocalypse(Skill):
    def __init__(self):
        Skill.__init__(self)
        self._name = 'Apocalypse'
        self._AOE = None
        self._size = 3
        self._cost = 4
        self._damage = 50
        self._range = 5
        self._sprite_sheet = None

def ListSkills():
    return set(['Horizontal', 'Vertical', 'Execution', 'Apocalypse'])