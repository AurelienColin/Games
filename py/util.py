from os.path import join
import json
from . import Character, Skill

def ObjToCoord(obj):
    """From an object, retourn it's coordinates

    Input:
    obj - object: tuple of:
        [0] : the actual object
        [1] : the coordinates (a tuple of int)
        [2] ; its type (sprite, map, or anything else), a string

    output:
    rect.height - int: height of the object
    rect.width - int: width of the object
    posX - int: px pos of the object (up left)
    pox_y - int: px pos of the object (up left)"""
    rect = obj[0].get_rect()
    posX, posY = obj[1]
    return rect.size, obj[1]

def StatCalculation(value):
    """Each point in value reduce the result by 0.4%
    Input:
    value - int

    Output:
    return int"""
    return pow(0.996, value)

def StatToStr(value):
    """Return the string representation
    Input:
    value - int

    Output:
    return str(int(float*100))"""
    return str(int((1-pow(0.996, value))*100))

def GetDirection(ini_tile, final_tile):
    """0 for up, 1 for left, 2 for down, 3 for right
    Input:
    ini_tile - tuple of two int: initial tile
    final_tile - tuple of two int: final tile

    Output:
    direction - int"""
    diff = final_tile[0] - ini_tile[0], final_tile[1] - ini_tile[1]
    x, y = diff
    if x>=0 and y>=0:
        if x>y:
            direction = 3
        else:
            direction = 2
    elif x>=0 and y<=0:
        if x>-y:
            direction = 3
        else:
            direction = 0
    elif x<=0 and y<=0:
        if -x>-y:
            direction = 1
        else:
            direction = 0
    elif x<=0 and y>=0:
        if -x>y:
            direction = 1
        else:
            direction = 2
    return direction

def FormatText(text, l):
    """Input:
    text - string
    l - int: number of letter on one line

    Output:
    list of string"""
    name, text = text.split(':')
    lines, line = [], ''
    for word in text.split():
        if len(line + word)+1 < l:
            line += word + ' '
        else:
            lines.append(line)
            line = word + ' '
    lines.append(line)
    return name + ': ' + '; '.join(lines)


def WeakAgainst(t_ini):
    """t_ini is weak against result[0]
       t_ini is strong against result[1]"""
    if t_ini == 'water':
        return ['earth', 'fire']
    elif t_ini == 'earth':
        return ['wind', 'water']
    elif t_ini == 'wind':
        return ['fire', 'earth']
    elif t_ini == 'fire':
        return ['water', 'wind']
    else:
        return [None, None]

def ReadJSON(folder, file):
    """Input:
    folder - a string
    file - string: the name of .json contening the object

    Output:
    object - Could be a skill or a character"""
    with open(join('json', folder, file+'.json'), 'r') as file:
        data = json.load(file)
        if 'skill' in data.keys():
            return Skill.Skill.FromJSON(data['skill'])
        elif 'character' in data.keys():
            return Character.Character.FromJSON(data['character'])

def WriteJSON(data, file):
    """Input:
    data - dictionary
    file - string

    Output:
    Nothing, but a .json is written"""
    folder = list(data.keys())[0] # Only one key aniway
    with open(join('res', 'json', folder, file+'.json'), 'w') as file:
        json.dump(data, file, sort_keys=True, indent=4)

