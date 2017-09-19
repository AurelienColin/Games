from os.path import join
import json

class Item():
    def __init__(self, file):
        self.FromJson(file)
        self.equiped = False
        pass

    def FromJson(self, file):
        with open(join('res','json', 'item', file+'.json'), 'r') as file:
            data = json.load(file)['item']
        self.name = data['name']
        self.cara = data['cara']
        self.cost = data['cost']
        if data['use']:
            self.use = data['use']
            self.usable = True
        else:
            self.use = {}
            self.usable = False
        self.durability = data['durability']
        for key in ['PA', 'PV', 'PM', 'strength', 'magic', 'defense', 'resistance', 'speed']:
            if key not in self.cara:
                self.cara[key]=0
            if key not in self.use:
                self.use[key]=0

    def ReduceDurability(self):
        self.durability-=1
        if self.durability == 0:
            self = Item("Broken Arte")