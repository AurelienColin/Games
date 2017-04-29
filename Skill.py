class Skill():
    def __init__(self):
        self._effects = {}
        pass

    def Initialization(name):
        if name == 'Execution':
            self = Execution()
        if name == 'Vertical':
            self = Vertical()
        if name == 'Horizontal':
            self = Horizontal()
        if name == 'Apocalypse':
            self = Apocalypse()
        else:
            self = None
        return self

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