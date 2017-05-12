
def ObjToCoord(obj):
    rect = obj[0].get_rect()
    pos_x, pos_y = obj[1]
    return rect.height, rect.width, pos_x, pos_y

def StatCalculation(value):
    return 1-pow(0.996, value)