import pygame
from os.path import join
from . import util, Map, Level

class TextBox():
    def __init__(self, box_file, texts, dim, pos, size=20, color=(0,0,0)):
        fullname = join('res', 'textbox', box_file)
        self.text = []
        self.string = []
        for j, text in enumerate(texts):
            text = text.split(';')
            self.string += [text[i] for i in range(len(text))]
            self.text += [Text(text[i], (pos[j][0], pos[j][1]+i*(size+2)),
                                size, color=color) for i in range(len(text))]
        self.size = dim
        self.imgs = False
        img = pygame.image.load(fullname)
        self.box = pygame.transform.smoothscale(img, dim)
        self.imgs = False

    def Initialization(name, screen = None, char=None):
        if name == 'MainMenu':
            self = MainMenu()
        elif name == 'Skills':
            self = SkillMenu(char)
        elif name == 'Status':
            self = StatusBox(screen)
            if screen.charBox == -1:
                screen.charBox = 0
        elif name == 'LauncherMenu':
            self = LauncherMenu()
        elif name == 'Level Selection':
            self = LevelSelection()
        elif name == 'Level0':
            Level.Level(screen, 'level0')
        elif name == 'Items':
            self = ItemsMenu(char)
        elif name in itemList():
            self = ItemMenu(char.getItem(name))
            screen.currentItem = name
        elif name == 'Use':
            char.UseItem(screen.currentItem, screen)
            self = DoneBox()
        elif name == 'Equip':
            char.Equip(screen.currentItem)
            self = DoneBox()
        elif name == 'Desequip':
            char.Desequip(screen.currentItem)
            self = DoneBox()
        return self

    def Update(self, texts, pos, size=20):
        self.string = []
        for j, text in enumerate(texts):
            text = text.split(';')
            self.string += [text[i] for i in range(len(text))]
            self.text += [Text(text[i], (pos[j][0], pos[j][1]+i*size), 20) for i in range(len(text))]

class Text():
    def __init__(self, text, pixel, size, color=(0,0,0)):
        font = pygame.font.SysFont('freesans', size)
        self.text = text
        self.string = font.render(text, True, color)
        self.pixel = pixel

class MainMenu(TextBox):
    def __init__(self):
        string = ["Aide;Skills;Items;Status;Exit;End Turn"]
        name = "TextBox_ExtraLarge.png"
        TextBox.__init__(self,name, string, (130,170), [(30, 20)])

class LauncherMenu(TextBox):
    def __init__(self):
        string = ['Level Selection']
        name = "Title1.png"
        TextBox.__init__(self,name, string, (200,50), [(45, 12)], color=(255,255,255))

class LevelSelection(TextBox):
    def __init__(self):
        string = ['Level0;Prologue;Level1;Epilogue']
        name = "TextBox_ExtraLarge.png"
        TextBox.__init__(self,name, string, (130,170), [(30, 20)])

class SkillMenu(TextBox):
    def __init__(self, character):
        skills = [skill.cara['name'] for skill in character.skills]
        string = [';'.join(skills)]
        name = "TextBox_ExtraLarge.png"
        TextBox.__init__(self, name, string, (130, 170), [(30, 20)])

class Status(TextBox):
    def __init__(self, character):
        data = [str(character.cara['name']),
                'PV: '+ str(character.cara['PV']) + '/' + str(character.cara['PV_max']),
                'PA: '+ str(character.cara['PA']) + '/' + str(character.cara['PA_max']),
                'PM: '+ str(character.cara['PM']) + '/' + str(character.cara['PM_max'])]
        string = [';'.join(data)]
        name = "TextBox_ExtraLarge.png"
        TextBox.__init__(self, name, string, (128,100), [(20, 10)], size =18)

    def Update(self, character):
        data = [str(character.cara['name']),
                'PV: '+ str(character.cara['PV']) + '/' + str(character.cara['PV_max']),
                'PA: '+ str(character.cara['PA']) + '/' + str(character.cara['PA_max']),
                'PM: '+ str(character.cara['PM']) + '/' + str(character.cara['PM_max'])]
        text = ';'.join(data)
        self.string = text.split(';')

class SkillDetails(TextBox):
    def __init__(self, skill, character):
        if skill.cara['type'] == 'magic':
            dmg = character.MagicalDmg(skill.cara['damage'])
        elif skill.cara['type'] == 'physic':
            dmg = character.PhysicalDmg(skill.cara['damage'])
        hit = str(int(skill.cara['hit']*character.getCara('hit')*100))
        data = [skill.cara['name'], 'Type: ' + skill.cara['type'], 'PA: ' + str(skill.cara['cost']),
                'Dmg: ' + str(int(dmg)), 'Hit: ' + hit]
        string = [';'.join(data)]
        name = "TextBox_ExtraLarge.png"
        TextBox.__init__(self, name, string, (128,100), [(20, 10)], size = 15)

class Portrait(TextBox):
    def __init__(self, chara):
        size = 200,230
        u = util.StatToStr
        data1 = [str(chara.cara['name']),
                'PV: '+ str(chara.cara['PV']) + '/' + str(chara.cara['PV_max']),
                'PA: '+ str(chara.cara['PA']) + '/' + str(chara.cara['PA_max']),
                'PM: '+ str(chara.cara['PM']) + '/' + str(chara.cara['PM_max'])]
        data2 = ['Str: ' + u(chara.cara['strength']), 'Mgc: ' + u(chara.cara['magic']),
                 'Def: ' + u(chara.cara['defense']), 'Res: ' + u(chara.cara['resistance']),
                 'Hit: ' + u(chara.cara['hit']), 'Avd: ' + u(chara.cara['avoid']),
                ' ;Lvl: ' + str(chara.cara['level'])]
        string = [';'.join(data1), ';'.join(data2)]
        name = "TextBox_ExtraLarge.png"
        TextBox.__init__(self, name, string, size, [(20, 10), (130, 10+18+2)], size = 18)
        self.imgs = [[chara.sprite['portrait'], (0, size[1]-128-12)]]

class IniList(TextBox):
    def __init__(self, characters, turns, turn):
        turns, i, j, temp = turns, turn, 0, []
        cap = 10
        margin = 37
        while j < len(characters)*2:
            if i in turns:
                j+=1
                temp.append(turns[i])
                k = turn + int(util.StatCalculation(turns[turn].cara['speed'])*100)
                while k in turns:
                    k+=1
                turns[k] = turns[i]
            i += 1
        size = margin*min(cap, len(characters)*2)+10,50
        name = "TextBox_LongSmall.png"
        TextBox.__init__(self, name, [''], size, [(0, 0)])
        self.imgs = []
        for i, character in enumerate(temp):
            self.imgs.append([character.sprite['static'], (5+i*margin, 10)])
            if i == cap:
                break

class StatusBox(TextBox):
    def __init__(self, screen):
        character = screen.characters[screen.charBox]
        c = character.cara
        u = util.StatToStr
        string = ['', '', '', '']
        size = 18
        pos = [(140, 30), (185, 30+2*(size+2)), (20, 140), (140, 140)]
        string[0] = 'Name: ' + str(c['name'])+ ';' + 'PV: ' + str(c['PV']) \
                    + '/' + str(c['PV_max']) + ';PA:' + str(c['PA_max']) \
                    +';Lvl: ' + str(u(c['level']))
        string[1] = 'PM: ' + str(c['PM_max'])
        string[2] = 'Str: ' + str(u(c['strength'])) +';Mgc: ' + str(u(c['magic'])) \
                    + ';Def: ' + str(u(c['defense'])) + ';Res: ' \
                    + str(u(c['resistance'])) + ';Spd: ' + str(u(c['speed'])) \
                    + ';Hit: ' + str(u(c['hit'])) + ';Avd: ' + str(u(c['avoid']))
        for skill in character.skills[:5]:
            string[3] +=skill.cara['name'] + ';'
        string[3] = string[3][:-1]  # Remove the last ';'
        name = 'TextBox_ExtraLarge.png'
        TextBox.__init__(self, name, string, (300, 300), pos, size=size)
        self.imgs = [[character.sprite['portrait'], (0, 0)]]

class ChildBox(TextBox):
    def __init__(self, choice):
        string = ''
        if choice[:4] == 'Name':
            if choice[6:] == 'Anna':
                string = 'Cute girl'
        elif choice[:3] == 'Lvl':
            string = 'Level of;the character'
        elif choice[:2] == 'PV':
            string = 'Quantity of;life remaining'
        elif choice[:2] == 'PA':
            string = 'Capacity to;act each turn'
        elif choice[:2] == 'PM':
            string = 'Capacity to;move each;turn'
        elif choice[:3] == 'Str':
            string = 'Increase the;dmg of phys.;attacks'
        elif choice[:3] == 'Def':
            string = 'Decrease the;dmg done by;phys. attacks'
        elif choice[:3] == 'Mgc':
            string = 'Increase the;dmg of mgc.;attacks'
        elif choice[:3] == 'Res':
            string = 'Decrease the;dmg done by;mgc. attacks'
        elif choice[:3] == 'Spd':
            string = 'Reduce the;time during;two turns'
        elif choice[:3] == 'Hit':
            string = 'Increase the;probability;of hit'
        elif choice[:3] == 'Avd':
            string = 'Decrease the;probability;of begin hit'
        name = "TextBox_ExtraLarge.png"
        TextBox.__init__(self, name, [string], (128,100), [(20, 10)], size=20)

class TileData(TextBox):
    def __init__(self, tile, mapData, tileSize):
        px = (tile[0]*tileSize, tile[1]*tileSize)
        name = str(Map.CheckProperties(px, 'name', mapData, tileSize))
        Def = str(Map.CheckProperties(px, 'Def', mapData, tileSize))
        Res = str(Map.CheckProperties(px, 'Res', mapData, tileSize))
        avoid = str(Map.CheckProperties(px, 'Avoid', mapData, tileSize))
        string = name +';def: ' + Def + ';res: ' + Res + ';avoid: ' + avoid
        name = "TextBox_ExtraLarge.png"
        TextBox.__init__(self, name, [string], (90,75), [(15, 3)], size=15)

class Dialog(TextBox):
    def __init__(self, text):
        char_name, string = text.split(':')
        name = 'TextBox_Large.png'
        TextBox.__init__(self, name, [char_name, string], (300,100),
                         [(15, 10), (20, 30)], size=17)

class LevelUp(TextBox):
    def __init__(self, character):
        c = character.cara
        name = 'Level_up.png'
        cname = c['name']
        title = 'LEVEL UP !'
        lvl = 'Lvl: '+str(c['level']) + ' + 1'
        PV = 'PV : ' + str(c['PV_max']) + ' + ' + str(c['growth']['PV'])
        Spd = 'Spd : ' + str(c['speed']) + ' + ' + str(c['growth']['speed'])
        Mgc = 'Mgc : ' + str(c['magic']) + ' + ' + str(c['growth']['magic'])
        Def = 'Def : ' + str(c['defense']) + ' + ' + str(c['growth']['defense'])
        Str = 'Str : ' + str(c['strength']) + ' + ' + str(c['growth']['strength'])
        Res = 'Res : ' + str(c['resistance']) + ' + ' + str(c['growth']['resistance'])
        string=[cname, lvl, PV, Spd, Str, Def, Mgc, Res, title]
        pos = [(45,29), (190,29), (45,62), (190,62), (45, 93), (190,93),
               (45,126), (190,126), (120, 8)]
        TextBox.__init__(self, name, string, (296,176), pos, size=13,
                         color=(255,255,255))

class ItemMenu(TextBox):
    def __init__(self, item):
        name = "TextBox_ExtraLarge.png"
        if item.equiped:
            string = "Desequip;Throw;Trade"
        else:
            string = "Equip;Throw;Trade"
        if item.usable:
            string += ';Use'
        TextBox.__init__(self,name, [string], (130,170), [(30, 20)])

class ItemsMenu(TextBox):
    def __init__(self, character):
        name = "TextBox_ExtraLarge.png"
        string = ""
        for place, item in character.items.items():
            string += item.name +';'
        if string[-1] == ';':
            string = string[:-1]
        TextBox.__init__(self,name, [string], (170,170), [(30, 20)])

class DoneBox(TextBox):
    def __init__(self):
        name = "TextBox_Small.png"
        TextBox.__init__(self,name, ["Done"], (80,50), [(20, 10)])


def itemList():
    return ['Carak Dae', 'Broken Artefact']
