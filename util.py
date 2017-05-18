
def ObjToCoord(obj):
    rect = obj[0].get_rect()
    pos_x, pos_y = obj[1]
    return rect.height, rect.width, pos_x, pos_y

def StatCalculation(value):
    return 1-pow(0.996, value)

def GetDirection(ini_tile, final_tile):
    """0 for up, 1 for left, 2 for down, 3 for right"""
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