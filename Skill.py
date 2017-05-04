import Highlight
import Screen
import Map
import numpy as np

class Skill():
    def __init__(self):
        self._effects = {}

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

    def Aim(self, character, screen, map_data, playerTeam):
        center = (int(character._pos[0]/screen._tile_size),
                  int(character._pos[1]/screen._tile_size))

        aimable = GetAimable(center, self._range,map_data, screen._tile_size, playerTeam, self._perce)
        highlighted = Highlight.HighlightTiles(screen._tile_size, aimable,
                                               60, (0, 0,255))
        blue = {}
        for pos in highlighted:
            blue[pos] = screen.AddHighlight(highlighted[pos])
        return blue

def GetAimable(pos, scope, map_data, tile_size, playerTeam, perce):
    aimable = set()
    p = 'slowness'
    for x in range(max(pos[0]-scope, 0), pos[0]+scope+1):
        diff_x = x-pos[0]
        for y in range(max(pos[1]-scope,0), pos[1]+scope+1):
            diff_y = y-pos[1]
            transparent = True
            if abs(diff_x) + abs(diff_y) > scope:
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
                    if not perce:
                        for character in playerTeam._character_opponent:
                            if character._pos_tile == (x_c, y_c):
                                transparent = False
                                break
                    if Map.CheckProperties((x_c*tile_size, y_c*tile_size), p, map_data, tile_size) != '1':
                        transparent = False
                        break
            if transparent:
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
        self._range = 10
        self._sprite_sheet = None
        self._perce = False

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
        self._perce = False

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
        self._perce = False

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
        self._perce = False

def ListSkills():
    return set(['Horizontal', 'Vertical', 'Execution', 'Apocalypse'])