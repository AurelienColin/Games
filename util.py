
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
    pos_x - int: px pos of the object (up left)
    pox_y - int: px pos of the object (up left)"""
    rect = obj[0].get_rect()
    pos_x, pos_y = obj[1]
    return rect.height, rect.width, pos_x, pos_y

def StatCalculation(value):
    """Each point in value reduce the result by 0.4%
    Input:
    value - int

    Output:
    return int"""
    return 1-pow(0.996, value)

def GetDirection(ini_tile, final_tile):
    """0 for up, 1 for left, 2 for down, 3 for right
    Input:
    ini_tile - tuple of two int: initial tile
    final_tile - tuple of two int: final tile

    Output:
    direction - int"""
    diff = final_tile[0] - ini_tile[0], final_tile[1] - ini_tile[1]
    if diff[0]>=0 and diff[1]>=0:
        if diff[0]>diff[1]:
            direction = 3
        else:
            direction = 2
    elif diff[0]>=0 and diff[1]<=0:
        if diff[0]>-diff[1]:
            direction = 3
        else:
            direction = 0
    elif diff[0]<=0 and diff[1]<=0:
        if -diff[0]>-diff[1]:
            direction = 1
        else:
            direction = 0
    elif diff[0]<=0 and diff[1]>=0:
        if -diff[0]>diff[1]:
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

