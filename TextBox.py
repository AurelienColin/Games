import pygame
from os.path import join
import util
import Map

class TextBox():
    def __init__(self, box_file, texts, height, width, pos, size=20):
        fullname = join('res', 'textbox', box_file)
        self._text = []
        self._string = []
        for j, text in enumerate(texts):
            text = text.split(';')
            self._string += [text[i] for i in range(len(text))]
            self._text += [Text(text[i], (pos[j][0], pos[j][1]+i*(size+2)), 20) for i in range(len(text))]
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
    def __init__(self, text, pos, size):
        font = pygame.font.SysFont('freesans', size)
        self._text = text
        self._string = font.render(text, True, (0,0,0))
        self._pos = pos

class MainMenu(TextBox):
    def __init__(self):
        string = ["Aide;Skills;Objets;Status;Exit;End Turn"]
        name = "TextBox_ExtraLarge.png"
        TextBox.__init__(self,name, string, 130, 170, [(30, 20)])

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
        TextBox.__init__(self, name, string, 128, 100, [(20, 10)], size =18)

    def Update(self, character):
        data = [str(character._cara['name']),
                'PV: '+ str(character._cara['PV']) + '/' + str(character._cara['PV_max']),
                'PA: '+ str(character._cara['PA']) + '/' + str(character._cara['PA_max']),
                'PM: '+ str(character._cara['PM']) + '/' + str(character._cara['PM_max'])]
        text = ';'.join(data)
        self._string = text.split(';')

class SkillDetails(TextBox):
    def __init__(self, skill):
        data = [skill._name, 'Type: ' + skill._type, 'PA: ' + str(skill._cost), 'Dmg: ' + str(skill._damage)]
        string = [';'.join(data)]
        name = "TextBox_ExtraLarge.png"
        TextBox.__init__(self, name, string, 128, 100, [(20, 10)], size = 15)

class Portrait(TextBox):
    def __init__(self, character):
        size = 128, 230
        data = [str(character._cara['name']),
                'PV: '+ str(character._cara['PV']) + '/' + str(character._cara['PV_max']),
                'PA: '+ str(character._cara['PA']) + '/' + str(character._cara['PA_max']),
                'PM: '+ str(character._cara['PM']) + '/' + str(character._cara['PM_max'])]
        string = [';'.join(data)]
        name = "TextBox_ExtraLarge.png"
        TextBox.__init__(self, name, string, size[0], size[1], [(20, 10)], size = 18)
        self._imgs = [[character._portrait, (0, size[1]-128-12)]]

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
        size = margin*min(cap, len(characters)*2)+10, 50
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
        string = ['', '', '', '']
        pos = [(140, 30), (180, 64), (20, 150), (140, 150)]
        string[0] = 'Name: ' + str(c['name']) + ';' + 'PV: ' + str(c['PV']) + '/' + str(c['PV_max']) + ';PA:' + str(c['PA_max'])
        string[1] = 'PM: ' + str(c['PM_max'])
        string[2] = 'Str: ' + str(c['strength']) +';Mgc: ' + str(c['magic']) + ';Def: ' + str(c['defense']) + ';Res: ' + str(c['resistance']) + ';Spd: ' + str(c['speed'])
        for skill in character._skills[:5]:
            string[3] +=skill._name + ';'
        string[3] = string[3][:-1]  # Remove the last ';'
        name = 'TextBox_ExtraLarge.png'
        TextBox.__init__(self, name, string, 300, 300, pos, size=15)
        self._imgs = [[character._portrait, (0, 0)]]

class ChildBox(TextBox):
    def __init__(self, choice):
        string = ''
        if choice[:4] == 'Name':
            if choice[6:] == 'Anna':
                string = 'Cute girl'
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
        name = "TextBox_ExtraLarge.png"
        TextBox.__init__(self, name, [string], 128, 100, [(20, 10)], size=13)

class TileData(TextBox):
    def __init__(self, tile_pos, map_data, tile_size):
        px_pos = (tile_pos[0]*tile_size, tile_pos[1]*tile_size)
        name = str(Map.CheckProperties(px_pos, 'name', map_data, tile_size))
        Def = str(Map.CheckProperties(px_pos, 'Def', map_data, tile_size))
        Res = str(Map.CheckProperties(px_pos, 'Res', map_data, tile_size))
        avoid = str(Map.CheckProperties(px_pos, 'Avoid', map_data, tile_size))
        string = name +';def: ' + Def + ';res: ' + Res + ';avoid: ' + avoid
        name = "TextBox_ExtraLarge.png"
        TextBox.__init__(self, name, [string], 90, 70, [(15, 0)], size=13)

class Dialog(TextBox):
    def __init__(self, text):
        char_name, string = text.split(':')

        name = 'TextBox_Large.png'
        TextBox.__init__(self, name, [char_name, string], 300, 100,
                         [(15, 10), (20, 30)], size=15)


def ListMenus():
    return set(['MainMenu', 'Skills', 'Status'])