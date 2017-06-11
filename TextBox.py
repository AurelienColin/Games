import pygame
from os.path import join
import util
import Map

class TextBox():
    def __init__(self, box_file, texts, width, height, pos, size=20, color=(0,0,0)):
        fullname = join('res', 'textbox', box_file)
        self._text = []
        self._string = []
        for j, text in enumerate(texts):
            text = text.split(';')
            self._string += [text[i] for i in range(len(text))]
            self._text += [Text(text[i], (pos[j][0], pos[j][1]+i*(size+2)),
                                size, color=color) for i in range(len(text))]
        self._height = height
        self._width = width
        self._imgs = False
        img = pygame.image.load(fullname)
        self._box = pygame.transform.smoothscale(img, (height, width))
        self._imgs = False

    def Initialization(name, screen = None, character=None):
        if name == 'MainMenu':
            self = MainMenu()
        elif name == 'Skills':
            self = SkillMenu(character)
        elif name == 'Status':
            self = StatusBox(screen)
            if screen._status_box == -1:
                screen._status_box = 0
        else:
            self = None
        return self

    def Update(self, texts, pos, size=20):
        self._string = []
        for j, text in enumerate(texts):
            text = text.split(';')
            self._string += [text[i] for i in range(len(text))]
            self._text += [Text(text[i], (pos[j][0], pos[j][1]+i*size), 20) for i in range(len(text))]

class Text():
    def __init__(self, text, pos, size, color=(0,0,0)):
        font = pygame.font.SysFont('freesans', size)
        self._text = text
        self._string = font.render(text, True, color)
        self._pos = pos

class MainMenu(TextBox):
    def __init__(self):
        string = ["Aide;Skills;Objets;Status;Exit;End Turn"]
        name = "TextBox_ExtraLarge.png"
        TextBox.__init__(self,name, string, 170, 130, [(30, 20)])

class SkillMenu(TextBox):
    def __init__(self, character):
        skills = [skill._name for skill in character._skills]
        string = [';'.join(skills)]
        name = "TextBox_ExtraLarge.png"
        TextBox.__init__(self, name, string, 150, 150, [(30, 30)])

class Status(TextBox):
    def __init__(self, character):
        data = [str(character._cara['name']),
                'PV: '+ str(character._cara['PV']) + '/' + str(character._cara['PV_max']),
                'PA: '+ str(character._cara['PA']) + '/' + str(character._cara['PA_max']),
                'PM: '+ str(character._cara['PM']) + '/' + str(character._cara['PM_max'])]
        string = [';'.join(data)]
        name = "TextBox_ExtraLarge.png"
        TextBox.__init__(self, name, string, 100, 128, [(20, 10)], size =18)

    def Update(self, character):
        data = [str(character._cara['name']),
                'PV: '+ str(character._cara['PV']) + '/' + str(character._cara['PV_max']),
                'PA: '+ str(character._cara['PA']) + '/' + str(character._cara['PA_max']),
                'PM: '+ str(character._cara['PM']) + '/' + str(character._cara['PM_max'])]
        text = ';'.join(data)
        self._string = text.split(';')

class SkillDetails(TextBox):
    def __init__(self, skill, character):
        if skill._type == 'magic':
            dmg = character.MagicalDmg(skill._damage)
        elif skill._type == 'physic':
            dmg = character.PhysicalDmg(skill._damage)
        hit = str(int(skill._hit*character.getCara('hit')*100))
        data = [skill._name, 'Type: ' + skill._type, 'PA: ' + str(skill._cost),
                'Dmg: ' + str(int(dmg)), 'Hit: ' + hit]
        string = [';'.join(data)]
        name = "TextBox_ExtraLarge.png"
        TextBox.__init__(self, name, string, 100, 128, [(20, 10)], size = 15)

class Portrait(TextBox):
    def __init__(self, chara):
        size = 230, 200
        u = util.StatToStr
        data1 = [str(chara._cara['name']),
                'PV: '+ str(chara._cara['PV']) + '/' + str(chara._cara['PV_max']),
                'PA: '+ str(chara._cara['PA']) + '/' + str(chara._cara['PA_max']),
                'PM: '+ str(chara._cara['PM']) + '/' + str(chara._cara['PM_max'])]
        data2 = ['Str: ' + u(chara._cara['strength']), 'Mgc: ' + u(chara._cara['magic']),
                 'Def: ' + u(chara._cara['defense']), 'Res: ' + u(chara._cara['resistance']),
                 'Hit: ' + u(chara._cara['hit']), 'Avd: ' + u(chara._cara['avoid']),
                ' ;Lvl: ' + str(chara._cara['level'])]
        string = [';'.join(data1), ';'.join(data2)]
        name = "TextBox_ExtraLarge.png"
        TextBox.__init__(self, name, string, size[0], size[1], [(20, 10), (130, 10+18+2)], size = 18)
        self._imgs = [[chara._portrait, (0, size[0]-128-12)]]

class IniList(TextBox):
    def __init__(self, characters, turns, turn):
        temp_turns, i, j, temp = turns, turn, 0, []
        cap = 10
        margin = 37
        while j < len(characters)*2:
            if i in temp_turns:
                j+=1
                temp.append(temp_turns[i])
                k = turn + int(util.StatCalculation(turns[turn]._cara['speed'])*100)
                while k in temp_turns:
                    k+=1
                temp_turns[k] = temp_turns[i]
            i += 1
        size = 50, margin*min(cap, len(characters)*2)+10
        name = "TextBox_LongSmall.png"
        TextBox.__init__(self, name, [''], size[0], size[1], [(0, 0)])
        self._imgs = []
        for i, character in enumerate(temp):
            self._imgs.append([character._sprite['static'], (5+i*margin, 10)])
            if i == cap:
                break

class StatusBox(TextBox):
    def __init__(self, screen):
        character = screen._characters[screen._status_box]
        c = character._cara
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
        for skill in character._skills[:5]:
            string[3] +=skill._name + ';'
        string[3] = string[3][:-1]  # Remove the last ';'
        name = 'TextBox_ExtraLarge.png'
        TextBox.__init__(self, name, string, 300, 300, pos, size=size)
        self._imgs = [[character._portrait, (0, 0)]]

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
        TextBox.__init__(self, name, [string], 100, 128, [(20, 10)], size=20)

class TileData(TextBox):
    def __init__(self, tile_pos, map_data, tile_size):
        px_pos = (tile_pos[0]*tile_size, tile_pos[1]*tile_size)
        name = str(Map.CheckProperties(px_pos, 'name', map_data, tile_size))
        Def = str(Map.CheckProperties(px_pos, 'Def', map_data, tile_size))
        Res = str(Map.CheckProperties(px_pos, 'Res', map_data, tile_size))
        avoid = str(Map.CheckProperties(px_pos, 'Avoid', map_data, tile_size))
        string = name +';def: ' + Def + ';res: ' + Res + ';avoid: ' + avoid
        name = "TextBox_ExtraLarge.png"
        TextBox.__init__(self, name, [string], 75, 90, [(15, 3)], size=15)

class Dialog(TextBox):
    def __init__(self, text):
        char_name, string = text.split(':')
        name = 'TextBox_Large.png'
        TextBox.__init__(self, name, [char_name, string], 100, 300,
                         [(15, 10), (20, 30)], size=17)

class LevelUp(TextBox):
    def __init__(self, character):
        c = character._cara
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
        TextBox.__init__(self, name, string, 176, 296, pos, size=13,
                         color=(255,255,255))

def ListMenus():
    return set(['MainMenu', 'Skills', 'Status'])