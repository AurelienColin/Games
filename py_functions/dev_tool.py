# -*- coding: utf-8 -*-
"""
Created on Wed Nov  8 21:41:08 2017

@author: Rignak
"""
from os.path import join, exists
from os import listdir
from json import load
import glob
from lxml import etree

def Error(file, key, reason, opt=False):
    s = 'Error in ' + str(file) + " : '"+ str(key)+"'"
    if reason == 0:
        s+= "is not a valid json"
    if reason == 1:
        s+= ' not defined'
    if reason == 2:
        s+= ' incorrect type'
        s+= " | expecting " + str(opt[0]) + ", got " + str(opt[1])
    if reason == 3:
        s+= " ressource not found"
    if reason == 4:
        s+= ' incorrect length'
        s+= " | expecting " + str(opt[0]) + ", got " + str(opt[1])
    print(s)
    return 1


def CheckExistence(file, data, key, folder):
    if key in data and type(data[key]) == str:  # If not, error message already printed
        if not exists(join(folder, data[key])):
            return Error(file, data[key], 3)
    return 0
                
def CheckValue(file, data, expected):
    e = 0
    for key, type_ in expected:
        if key not in data:
            e += Error(file, key, 1)
        elif type_ != type(data[key]):
            e += Error(file, key, 2, opt = (type_, type(data[key])))
    return e
            

def CheckUniDic(file, data, key1, type_):
    e = 0
    if key1 in data:  # If not, error message already printed
        for key2, v in data[key1].items():
            if type(type_)== list:
                if type(v)!=list:
                    e += Error(file, [key1, key2], 2, opt = (list, type(v)))
                elif len(v)!= len(type_):
                    e += Error(file, [key1, key2], 4, opt = (len(type_), len(v)))
                else:
                    for i in range(len(type_)):
                        if type_[i]!= type(v[i]):
                            e += Error(file, [key1, key2, i], 2, opt = (type_[i], type(v[i])))
            elif type_ != type(v):
                e += Error(file, [key1, key2], 2, opt = (type_, type(v)))
    return e

def CheckCmnDic(file, data, rules):
    e = 0
    for key, type_ in rules:
        v = data[key]
        if type(type_)== list:
            if type(v)!=list:
                e += Error(file, key, 2, opt = (list, type(v)))
            elif len(v)!= len(type_):
                e += Error(file, key, 4, opt = (len(type_), len(v)))
            else:
                for i in range(len(type_)):
                    if type_[i]!= type(v[i]):
                        e += Error(file, [key, i], 2, opt = (type_[i], type(v[i])))
        elif type_ != type(v):
            e += Error(file, key, 2, opt = (type_, type(v)))
    return e
    
def CheckItem(item):
    with open(join('..', 'res', 'json', 'item', item), 'r') as file:
        try:
            data = load(file)
        except:
            Error(item, item, '', 0)
            return 1
    if 'item' in data:
        e = 0
        data = data['item']
        expected = [['name', str], ['cara', dict], ['durability', int], ['cost', int],
                    ['use', dict], ['sound', str]]
        e += CheckValue(item, data, expected)
        
        e += CheckExistence(item, data, 'sound', join('..', 'res', 'sound'))
        e += CheckUniDic(item, data, 'use', [int, int])
        e += CheckUniDic(item, data, 'cara', int)
        return e
    else:
        return Error(item, item, 'item', 1)

def CheckList(file, key, l, rules):
    e = 0
    for i in range(len(l)):
        for j in range(len(rules)):
            if type(l[i][j]) != rules[j]:
                e += Error(file, [key,(i,j)], 2, opt = (rules[j], type(l[i][j])))
    return e
        
                
def CheckSkill(skill):
    with open(join('..', 'res', 'json', 'skill', skill), 'r') as file:
        try:
            data = load(file)
        except:
            return Error(skill, skill, '', 0)
    if 'skill' in data:
        e = 0
        data = data['skill']
        expected = [['sheet', str], ['sound', str]]
        e += CheckExistence(skill, data, 'sheet', join('..', 'res', 'sprite', 'effect'))
        e += CheckExistence(skill, data, 'sound', join('..', 'res', 'sound'))
        e += CheckValue(skill, data, expected)
        
        expected = [["rows", int], ['cols', int], ['action', [int, int]]]
        e += CheckCmnDic(skill, data['sprite'], expected)
        
        expected = [['name', str], ['AOE', str], ['size', int], ['cost', int],
                    ['damage', int], ['range', int], ['perce', bool], ['type', str],
                    ['ele', str], ['hit', float]]
        e += CheckCmnDic(skill, data['cara'], expected)
        
        expected = [['type', str], ['duration', int], ['power', int]]
        for key in ['effects', 'tileEffects']:
            for dic in data[key]:
                e +=  CheckCmnDic(skill, dic, expected)
        return e
    else:
        
        return Error(skill, skill, 'skill', 1)

def CheckCharacter(character):
    with open(join('..', 'res', 'json', 'character', character), 'r') as file:
        try:
            data = load(file)
        except:
            return Error(character, character, '', 0)
    if 'character' in data:
        e = 0
        data = data['character']
        
        expected = [['cara', dict], ['sheet', str], ["skill", list], 
                     ['sprite', dict], ['items' ,list], ['drop', list]]
        e += CheckValue(character, data, expected)
        
        e += CheckList(character, 'skill', data['skill'], [str, int])
        e += CheckList(character, 'drop', data['drop'], [str, float])
        e += CheckList(character, 'items', data['items'], [str, bool])
        e += CheckExistence(character, data, 'sheet', join('..', 'res', 'sprite', 'sheet'))
        e += CheckExistence(character, data['sprite'], 'portrait', join('..', 'res', 'sprite', 'portrait'))
        
        expected = [['attacking', [int, int]], ['cols', int], ['portrait', str],
                    ['rows', int], ['standing', [int, int]],['static', [int]],
                    ['static_down', [int]], ['static_left', [int]], ['static_right', [int]],
                    ['static_up', [int]], ['walking_down', [int, int]], ['walking_left', [int, int]],
                    ['walking_right', [int, int]], ['walking_up', [int, int]]]
        e += CheckCmnDic(character, data['sprite'], expected)
                
        expected = [['PA', int], ['PA_max', int], ['PM', int], ['PM_max', int],
                    ['PV', int], ['PV_max', int], ['avoid', int], ['defense', int],
                    ['elementalRes', dict], ['growth', dict], ['hit', int],
                    ['level', int], ['magic', int], ['name', str],
                    ['resPA', int], ['resPM', int], ['resistance', int], ['sex', str],
                    ['speed', int], ['strength', int], ['type', str], ['xp', dict],
                    ['effects', list]]
        e += CheckCmnDic(character, data['cara'], expected)
        e += CheckUniDic(character, data['cara'], 'elementRes', int)
        e += CheckUniDic(character, data['cara'], 'growth', int)
        e += CheckUniDic(character, data['cara'], 'xp', int)
        
        if data['cara']['sex'] not in ['f', 'm']:
            e += Error(character, ['cara', 'sex'], 2, opt=[['f', 'm'], data['cara']['sex']])
        expected = [['type', str], ['duration', int], ['power', int]]
        for dic in data['cara']['effects']:
            e +=  CheckCmnDic(character, dic, expected)
        for skill, level in data['skill']:
            if not exists(join('..', 'res', 'json', 'skill', skill+'.json')):
                e += Error(character, ['skill', skill+'.json'], 3)
        for item, b in data['items']:
            if not exists(join('..', 'res', 'json', 'item', item+'.json')):
                e += Error(character, ['item', item+'.json'], 3)
        for item, p in data['drop']:
            if not exists(join('..', 'res', 'json', 'item', item+'.json')):
                e += Error(character, ['drop', item+'.json'], 3)
        return e
            
    else:
        return Error(character, character, 'character', 1)
        
def CheckScript(script):
    with open(join('..', 'res', 'script', script), 'r') as file:
        lines = file.readlines()
    e = 0
    music = False
    characters = []
    for i, line in enumerate(lines):
        line = line.split()
        if ':' not in line[0]:
            if line[0] == 'music_on':
                if len(line) != 2:
                    e += Error(script, i+1, 3)
                elif not exists(join('..', 'res', 'music', line[1])):
                    e += Error(script, [i+1, line[1]], 3)
                else:
                    music = line[1]
            elif line[0] == 'music_off':
                if len(line) != 1:
                    e += Error(script, i+1, 3)
                elif music:
                    music = False
                else:
                    e += Error(script, [i+1, 'music_off'], -1)
            elif line[0] == 'sound':
                if len(line) != 2:
                    e += Error(script, i+1, 3)
                elif not exists(join('..', 'res', 'sound', line[1])):
                    e += Error(script, [i, line[1]], 3)
            elif line[0] == 'enter':
                if len(line) != 5:
                    e += Error(script, i+1, 4, opt=(5, len(line)))
                elif not exists(join('..', 'res', 'sprite', line[2])):
                    e += Error(script, [i, line[2]], 3)
                elif line[1] in characters:
                    e += Error(script, [i+1, line[1]], -1)
                else:
                    characters.append(line[1])
            elif line[0] == 'leave':
                if len(line) != 2:
                    e += Error(script, i+1, 3)
                elif line[1] not in characters:
                    e += Error(script, [i+1, line[1]], -1)
                else:
                    characters.pop(characters.index(line[1]))
            else:
                e += Error(script, [i+1, line[0]], -1)
        elif line[0][:-1] not in characters+['Narrator']:
            e += Error(script, [i+1, line[0]], -1)
        elif len(' '.join(line[1:])) > 90:
            e += Error(script, i+1, 4, opt=[90, len(' '.join(line[1:]))])
    return e

def CheckLevel(level):
    with open(join('..', 'res', 'json', 'level', level), 'r') as file:
        try:
            data = load(file)
        except:
            return Error(level, level, 0)
    if 'level' in data:
        data = data['level']
        e = 0
        expected = [['map', str], ['victories', list], ['script', str], ['characters', list],
                    ['initial_tiles', list], ['music', dict]]
        e += CheckValue(level, data, expected)
        
        expected = [['condition', str], ['next_level', str]]
        for dic in data['victories']:
            e +=  CheckCmnDic(level, dic, expected)
        
        expected = [['name', str], ['initial', [int, int]], ['team', int],
                    ['ia', str], ['leader', bool], ['coef', float], ['level', int],
                    ['items', list]]
        for dic in data['characters']:
            e +=  CheckCmnDic(level, dic, expected)
            for item in dic['items']:
                if not exists(join('..', 'res', 'json', 'item', item+'.json')):
                    e += Error(level, ['item', item+'.json'], 3)
            
        expected = [['placement', str], ['TRPG', str]]
        e +=  CheckCmnDic(level, data['music'], expected)
        
        e += CheckExistence(level, data, 'map', join('..', 'res', 'map'))
        e += CheckExistence(level, data, 'script', join('..', 'res', 'script'))
        e += CheckExistence(level, data['music'], 'TRPG', join('..', 'res', 'music'))
        e += CheckExistence(level, data['music'], 'placement', join('..', 'res', 'music'))
        for dic in data['victories']:
            e += CheckExistence(level, dic, 'next_level', join('..', 'res', 'json', 'level'))
            if dic['condition'] not in ["destroy", "kill leaders"]:
                e += Error(level, 'condition', 2, [["destroy", "kill leaders"], dic['condition']])
        for dic in data['characters']:
            if dic['ia'] not in ['null', 'defensif', 'aggressif', 'passif']:
                e += Error(level, 'condition', 2, [['null', 'defensif', 'aggressif', 'passif'], dic['ia']])
            e += CheckExistence(level, dic, 'name', join('..', 'res', 'json', 'character'))
        return e
    else:
        return 1

def CheckTSX(tsx):
    e = 0
    with open(join('..','res','map', '_rules.json'), 'r') as file:
        rules = load(file)
    tree = etree.parse(tsx)
    for properties in tree.xpath("/tileset/tile/properties"):
        for property_ in properties.findall('property'):
            if  property_.get('name') == 'name' and property_.get('value') not in rules:
                e += Error(tsx, property_.get('value'), 1)
                rules[property_.get('value')] = 'detected'
    return e
    
if __name__ == '__main__':
    e = 0
    print('----Check items')
    for item in listdir(join('..', 'res', 'json', 'item')):
        e += CheckItem(item)
    print('----Check skills')
    for skill in listdir(join('..', 'res', 'json', 'skill')):
        e += CheckSkill(skill)
    print('----Check characters')
    for character in listdir(join('..', 'res', 'json', 'character')):
        e += CheckCharacter(character)
    print('----Check script')
    for script in listdir(join('..', 'res', 'script')):
        e += CheckScript(script)
    print('----Check level')
    for level in listdir(join('..', 'res', 'json', 'level')):
        e += CheckLevel(level)
    print('----Check maps')
    for file in glob.glob(join('..','res','map', '*.tsx')):
        e += CheckTSX(file)
    print('\nEnd with', e, 'errors')