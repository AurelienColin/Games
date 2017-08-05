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
            self.usable = False
        self.durability = data['durability']

    def ReduceDurability(self):
        self.durability-=1
        if self.durability == 0:
            self = Item("Broken Arte")