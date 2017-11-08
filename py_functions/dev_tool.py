# -*- coding: utf-8 -*-
"""
Created on Wed Nov  8 21:41:08 2017

@author: Rignak
"""
from os.path import join, exists
from os import listdir
from json import load

def Error(file, key, reason, opt=False):
    s = 'Error in ' + str(file) + " : '"+ str(key)+"'"
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

def CheckScript():
    pass

def CheckExistence(data, key, folder):
    if key in data and type(data[key]) == str:  # If not, error message already printed
            if not exists(join('..', 'res', 'sound', data['sound'])):
                Error(item, 'sound', 3)
                return 1
    return 0
                
def CheckValue(data, expected):
    e = 0
    for key, type_ in expected:
        if key not in data:
            Error(item, key, 1)
            e += 1
        elif type_ != type(data[key]):
            Error(item, key, 2, opt = (type_, type(data[key])))
            e += 1
    return e
            

def CheckDic(data, expected):
    e = 0
    for key, e_type in expected:
        if key in data:  # If not, error message already printed
            for key2, v in data[key].items():
                if type(e_type)== list:
                    if type(v)!=list:
                        Error(item, [key, key2], 2, opt = (list, type(v)))
                        e += 1
                    elif len(v)!= len(e_type):
                        Error(item, [key, key2], 4, opt = (len(e_type), len(v)))
                        e += 1
                    else:
                        for i in range(len(e_type)):
                            if e_type[i]!= type(v[i]):
                                Error(item, [key, key2, i], 2, opt = (e_type[i], type(v[i])))
                                e += 1
    return e

    
def CheckItem(item):
    with open(join('..', 'res', 'json', 'item', item), 'r') as file:
        data = load(file)
    if 'item' in data:
        e = 0
        data = data['item']
        expected = [['name', str], ['cara', dict], ['durability', int], ['cost', int],
                    ['use', dict], ['sound', str]]
        e += CheckValue(data, expected)
        
        e += CheckExistence(data, 'sound', join('..', 'res', 'sound'))
        e += CheckDic(data, [['cara', int],['use', [int, int]]])
                                    
    else:
        Error(item, 'item', 1)
        e = 1
    return e

def CheckSkill():
    pass

def CheckCharacter():
    pass

def CheckLevel():
    pass

if __name__ == '__main__':
    e = 0
    items = listdir(join('..', 'res', 'json', 'item'))
    for item in items:
        e += CheckItem(item)
    print('End with', e, 'errors')
# Check char before script
# Check item & skill before char
# Check cara & level before level
# item, skill -> chara -> script -> level