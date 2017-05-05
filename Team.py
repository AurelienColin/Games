class Team():
    def __init__(self, nb, characters, tile_size):
        self._number = nb
        self._team_allies = []
        self._character_allies = []
        self._team_opponent = []
        self._character_opponent = []
        self._members = characters
        self._pos = [character._pos_tile for character in characters]

    def relations(self, teams):
        for team in teams:
            if team._number in self._team_opponent:
                for character in team._members:
                    self._character_opponent.append(character)
            if team._number in self._team_allies:
                for character in team._members:
                    self._character_allies.append(character)