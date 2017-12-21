import pygame
from os.path import join
from . import util, Map, Level

class TextBox():
    def __init__(self, files, texts, dim, text_pos, pos, size=20, color={'default':(0,0,0)}):
        names = [join('res', 'textbox', file) for file in files]
        self.text = []
        self.string = []
        c = color['default']
        for j, text in enumerate(texts):
            text = text.split(';')
            self.string += [text[i] for i in range(len(text))]
            self.text += [Text(text[i], (text_pos[j][0], text_pos[j][1]+i*(size+2)),
                          size, color=c) for i in range(len(text))]
        for i, c in color.items():
            if type(i)==int:
                if i < 0:
                    i = len(self.text)+i
                self.text[i].ChangeColor(c)

        self.size = dim
        self.imgs = False
        f1, f2 = pygame.transform.smoothscale, pygame.image.load
        self.box = [f1(f2(names[i]), self.size[i]) for i in range(len(names))]
        self.imgs = False




        if pos[0] == "middle":  # pos[1] == screen.size
            posX = int((pos[1][0] - self.size[0][0])/2)
            posY = int((pos[1][1] - self.size[0][1])/2)
            self.pos = [(posX, posY)]
        else:
            self.pos = pos

        screenDim = (870,870)
        decal = [min(0, screenDim[0]-self.size[0][0]-self.pos[0][0]),
                 min(0, screenDim[1]-self.size[0][1]-self.pos[0][1])]
        for i, xy in enumerate(self.pos):
            self.pos[i] = [xy[0]+decal[0], xy[1]+decal[1]]

    def Initialization(name, pos, screen = None, char=None):
        if name == 'MainMenu':
            self = MainMenu(pos)
        elif name == 'Skills':
            self = SkillMenu(char, pos)
        elif name == 'Status':
            self = StatusBox(screen, pos)
            if screen.charBox == -1:
                screen.charBox = 0
        elif name == 'LauncherMenu':
            self = LauncherMenu(pos)
        elif name == 'Level Selection':
            self = LevelSelection(pos)
        elif name in levelList():
            Level.Level(screen, name+'.json')
        elif name == 'Items':
            self = ItemsMenu(char, pos)
        elif name in itemList():
            if char.getItem(name):
                self = ItemMenu(char.getItem(name), pos)
                screen.currentItem = name
            else:
                self = ExitBox(pos)

        elif name == 'Use':
            char.UseItem(screen.currentItem, screen)
            self = ExitBox(pos)
        elif name == 'Equip':
            char.Equip(screen.currentItem)
            self = ExitBox(pos)
        elif name == 'Desequip':
            char.Desequip(screen.currentItem)
            self = ExitBox(pos)
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
        self.size = size
        self.text = text
        self.string = font.render(text, True, color)
        self.pixel = pixel

    def ChangeColor(self, color):
        font = pygame.font.SysFont('freesans', self.size)
        self.string = font.render(self.text, True, color)

class MainMenu(TextBox):
    def __init__(self, pos):
        string = ["Skills;Items;Status;Exit;End Turn"]
        box = ["TextBox_ExtraLarge.png"]
        TextBox.__init__(self,box, string, [(130,170)], [(30, 20)], pos)

class LauncherMenu(TextBox):
    def __init__(self, pos):
        string = ['Level Selection']
        box = ["Title1.png"]
        c = {'default':(255,255,255)}
        TextBox.__init__(self,box, string, [(200,50)], [(45, 12)], pos, color=c)

class LevelSelection(TextBox):
    def __init__(self, pos):
        string = ['Level0;Prologue;Level1;VisualNovel']
        string = ['Level1;VisualNovel']
        box = ["TextBox_ExtraLarge.png"]
        TextBox.__init__(self,box, string, [(130,170)], [(30, 20)], pos)

class SkillMenu(TextBox):
    def __init__(self, character, pos):
        skills = [skill.cara['name'] for skill in character.skills]
        string = [';'.join(skills)]
        box = ["TextBox_ExtraLarge.png"]
        TextBox.__init__(self, box, string, [(130, 170)], [(30, 20)], pos)

class Status(TextBox):
    def __init__(self, character, pos):
        data = [str(character.cara['name']),
                'PV: '+ str(character.cara['PV']) + '/' + str(character.cara['PV_max']),
                'PA: '+ str(character.cara['PA']) + '/' + str(character.cara['PA_max']),
                'PM: '+ str(character.cara['PM']) + '/' + str(character.cara['PM_max'])]
        string = [';'.join(data)]
        box = ["TextBox_ExtraLarge.png"]
        TextBox.__init__(self, box, string, [(128,100)], [(20, 10)], pos, size =18)

    def Update(self, character):
        data = [str(character.cara['name']),
                'PV: '+ str(character.cara['PV']) + '/' + str(character.cara['PV_max']),
                'PA: '+ str(character.cara['PA']) + '/' + str(character.cara['PA_max']),
                'PM: '+ str(character.cara['PM']) + '/' + str(character.cara['PM_max'])]
        text = ';'.join(data)
        self.string = text.split(';')

class SkillDetails(TextBox):
    def __init__(self, skill, character, pos):
        if skill.cara['type'] == 'magic':
            dmg = character.MagicalDmg(skill.cara['damage'])
        elif skill.cara['type'] == 'physic':
            dmg = character.PhysicalDmg(skill.cara['damage'])
        hit = str(int(skill.cara['hit']*character.getCara('hit')*100))
        data = [skill.cara['name'], 'Type: ' + skill.cara['type'], 'PA: ' + str(skill.cara['cost']),
                'Dmg: ' + str(int(dmg)), 'Hit: ' + hit]
        string = [';'.join(data)]
        box = ["TextBox_ExtraLarge.png"]
        TextBox.__init__(self, box, string, [(128,100)], [(20, 10)], pos, size = 15)

class ItemDetails(TextBox):
    def __init__(self, item, pos):
        data = ['       -- Passif --;', 'PA: ', item.cara['PA'], '; PM: ', item.cara['PM'], ';']+\
            ['Str: ', item.cara['strength'], '; Mgc: ', item.cara['magic'], ';']+\
            ['Def: ', item.cara['defense'], '; Res: ', item.cara['resistance'], ';']+\
            ['Spd: ', item.cara['speed'], ';PV: ', item.cara['PV'], ';']+\
            ['       -- Actif --;', 'PV: ', item.use['PV'], ';PM: ', item.use['PM'], ';']+\
            ['Str: ', item.use['strength'], ';Mgc: ', item.use['magic'], ';']+\
            ['Def: ', item.use['defense'], ';Res: ', item.use['resistance'], ';']+\
            ['Spd: ', item.use['speed'], ';PV: ', item.use['PV'], ';']+\
            ['Cost: ', item.cost]
        string = [''.join([str(ele) for ele in data])]
        box = ["TextBox_ExtraLarge.png"]
        TextBox.__init__(self, box, string, [(128,370)], [(20, 20)], pos, size = 15)

class Portrait(TextBox):
    def __init__(self, chara, pos):
        size = [(200,230)]
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
        box = ["TextBox_ExtraLarge.png"]
        TextBox.__init__(self, box, string, size, [(20, 10), (130, 10+18+2)], pos, size = 18)
        self.imgs = [[chara.sprite['portrait'], (0, size[0][1]-128-12)]]

class IniList(TextBox):
    def __init__(self, characters, turns, turn, pos):
        turns, i, j, temp = turns, turn, 0, []
        cap = 10
        margin = 37
        while j < len(characters)*2:
            if i in turns and not turns[i].dead:
                j+=1
                temp.append(turns[i])
                k = turn + int(util.StatCalculation(turns[turn].cara['speed'])*100)
                while k in turns:
                    k+=1
                turns[k] = turns[i]
            i += 1
        size = [(margin*min(cap, len(characters)*2)+10,50)]
        box = ["TextBox_LongSmall.png"]
        TextBox.__init__(self, box, [''], size, [(0, 0)], pos)
        self.imgs = []
        for i, character in enumerate(temp):
            self.imgs.append([character.sprite['static'], (5+i*margin, 10)])
            if i == cap:
                break

class StatusBox(TextBox):
    def __init__(self, screen, pos):
        character = screen.characters[screen.charBox]
        c = character.cara
        u = util.StatToStr
        string = ['', '', '', '']
        font_size = 18
        text_pos = [(140, 30), (185, 30+2*(font_size+2)), (20, 140), (140, 140)]
        string[0] = 'Name: ' + str(c['name'])+ ';' + 'PV: ' + str(c['PV']) \
                    + '/' + str(c['PV_max']) + ';PA:' + str(c['PA_max']) \
                    +';Lvl: ' + str(u(c['level']))
        string[1] = 'PM: ' + str(c['PM_max'])
        string[2] = 'Str: ' + str(u(c['strength'])) +';Mgc: ' + str(u(c['magic'])) \
                    + ';Def: ' + str(u(c['defense'])) + ';Res: ' \
                    + str(u(c['resistance'])) + ';Spd: ' + str(u(c['speed'])) \
                    + ';Hit: ' + str(u(c['hit'])) + ';Avd: ' + str(u(c['avoid']))
        for skill in character.skills[:5]:
            string[3] +=' '+skill.cara['name'] + ';'
        string[3] = string[3][:-1]  # Remove the last ';'
        temp = []
        for item in character.items:
            if item.usable:
                temp.append(' ' + item.name +'  '+ str(item.durability))
            else:
                temp.append(' ' + item.name)
        string+=temp
        box = ["TextBox_ExtraLarge.png", "Level_up.png"]
        size = [(300, 300), (296,176)]
        if pos[0] == "middle":  # pos[1] == screen.size
            posX = int((pos[1][0] - (size[0][0]))/2)
            posY = int((pos[1][1] - (size[0][1]+size[1][1]))/2)
            pos = [(posX, posY)]
        pos = pos + [(pos[0][0], pos[0][1]+size[0][1])]
        text_pos += [(30,327), (175,327), (30,360), (175,360), (30, 391), (175,391),
               (30,424), (175,424)]#[:len(character.items)]
        c = {'default':(0,0,0)}
        for i in range(-len(character.items),0):
            c[i]=(255,255,255)
        TextBox.__init__(self, box, string, size, text_pos, pos, size=font_size, color=c)
        self.imgs = [[character.sprite['portrait'], (0, 0)]]

class ChildBox(TextBox):
    def __init__(self, choice, pos):
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
        box = ["TextBox_ExtraLarge.png"]
        TextBox.__init__(self, box, [string], [(128,100)], [(20, 10)], pos, size=20)

class TileData(TextBox):
    def __init__(self, tile, mapData, tileSize, pos):
        px = (tile[0]*tileSize, tile[1]*tileSize)
        name = str(Map.CheckProperties(px, 'name', mapData, tileSize))
        Def = str(Map.CheckProperties(px, 'Def', mapData, tileSize))
        Res = str(Map.CheckProperties(px, 'Res', mapData, tileSize))
        avoid = str(Map.CheckProperties(px, 'Avoid', mapData, tileSize))
        string = name +';def: ' + Def + ';res: ' + Res + ';avoid: ' + avoid
        box = ["TextBox_ExtraLarge.png"]
        TextBox.__init__(self, box, [string], [(90,75)], [(15, 3)], pos, size=15)

class Dialog(TextBox):
    def __init__(self, text, pos):
        char_name, string = text.split(':')
        box = ['TextBox_Large.png']
        TextBox.__init__(self, box, [char_name, string], [(300,100)],
                         [(15, 10), (20, 30)], pos, size=17)

class LevelUp(TextBox):
    def __init__(self, character, pos):
        c = character.cara
        box = ['Level_up.png']
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
        text_pos = [(45,29), (190,29), (45,62), (190,62), (45, 93), (190,93),
               (45,126), (190,126), (120, 8)]
        c = {'default':(255,255,255)}
        TextBox.__init__(self, box, string, [(296,176)], text_pos, pos, size=13,
                         color=c)
class Drop(TextBox):
    def __init__(self, drop, pos):
        box = ['Level_up.png']
        string = drop
        text_pos = [(190,29), (45,62), (190,62), (45, 93), (190,93), (45,126),
               (190,126)][:len(drop)]
        c = {'default':(255,255,255)}
        TextBox.__init__(self, box, string, [(296,176)], text_pos, pos, size=13,
                         color=c)

class ItemMenu(TextBox):
    def __init__(self, item, pos):
        box = ["TextBox_ExtraLarge.png"]
        if item.equiped:
            string = "Desequip;Throw;Trade"
        else:
            string = "Equip;Throw;Trade"
        if item.usable:
            string += ';Use'
        TextBox.__init__(self,box, [string], [(130,170)], [(30, 20)], pos)

class ItemsMenu(TextBox):
    def __init__(self, character, pos):
        box = ["TextBox_ExtraLarge.png"]
        string = ';'.join([item.name for item in character.items])
        TextBox.__init__(self,box, [string], [(170,205)], [(20, 15)], pos)

class ExitBox(TextBox):
    def __init__(self, pos):
        box = ["TextBox_Small.png"]
        TextBox.__init__(self,box, ["Exit"], [(80,50)], [(20, 10)], pos)


def itemList():
    return ['Carak Dae', 'Broken Artefact', 'Potion']

def levelList():
    return ['Level1', 'VisualNovel']