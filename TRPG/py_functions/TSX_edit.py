# -*- coding: utf-8 -*-
"""
Created on Sun Nov 12 22:17:17 2017

@author: Rignak
"""

import json
from os.path import join
import glob
from lxml import etree

def Edit():
    with open(join('..','res','map', '_rules.json'), 'r') as file:
        data = json.load(file)
    for file in glob.glob(join('..','res','map', '*.tsx')):
        tree = etree.parse(file)
        for properties in tree.xpath("/tileset/tile/properties"):
            for property_ in properties.findall('property'):
                name = property_.get('name')
                if name == 'name':
                    values = data[property_.get('value')]
                    for property_2 in properties.findall('property'):
                        properties.remove(property_2)
                    e = etree.SubElement(properties, 'property')
                    e.set('name', 'name')
                    e.set('value', property_.get('value'))
                    e.set('type', 'str')
                    for k, v in values.items():
                        ef = etree.SubElement(properties, 'property')
                        ef.set('name', k)
                        ef.set('value', str(v))
                        if k in ['type']:
                            ef.set('type', 'str')
                        elif k in ['Def', 'Res', 'Avoid']:
                            ef.set('type', 'int')
                    break
        tree.write(file[:-4]+'_bis'+file[-4:])
if __name__ == '__main__':
    Edit()