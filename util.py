
def ObjToCoord(obj):
    rect = obj[0].get_rect()
    pos_x, pos_y = obj[1]
    return rect.height, rect.width, pos_x, pos_y

def Attack(current_character, skill, tiles, team, map_data):
    characters = team._character_allies + team._character_opponent + team._members
    print(characters)
    affected = []
    for character in characters:
        if character._pos_tile in tiles:
            affected.append(character)
    skill.Affect(current_character, affected, tiles, map_data)