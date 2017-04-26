class Character():
    def __init__(self):
        self._name = "Anna"
        self._class = 'Aventurier'
        self._sex = 'f'
        self._niveau = 1
        self._maxPV = 100
        self._PV = 100
        self._regen = 0
        self._sprite_sheet = "Res\\63468.png"
        self._maxPA = 6
        self._PA = self._maxPA
        self._maxPM = 4
        self._PM = self._maxPM
        self._active_skills = [Skill()]
        self._passive_skills = []
        self._XP = 0
        self._effects = []

    def UsePM(self, slowness):
        if slowness < self._PM:
            self._PM -= slowness
            return True
        else:
            return False

    def UsePA(self, cost):
        if cost < self._PA:
            self._PA -= cost
            return True
        else:
            return False

    def NewTurn(self):
        self._PV = max(self._maxPV, self._PV + self._regen)
        self._PA = self._maxPA
        self._PM = self._maxPM
