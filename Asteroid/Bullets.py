import math

from Rignak_Games.Entities import Entity


class Bullet(Entity):
    def __init__(self, ship, bullet_sprite_filename):
        x = ship.sprite.x + ship.sprite.original_size[0]//2
        y = ship.sprite.y + ship.sprite.original_size[1]//2
        ship_radian_angle = ship.sprite.angle / 180 * math.pi

        x_speed = ship.x_speed + ship.bullet_speed * math.cos(ship_radian_angle)
        y_speed = ship.x_speed - ship.bullet_speed * math.sin(ship_radian_angle)
        angle = math.atan(-y_speed / x_speed) / math.pi * 180
        angle_speed = 0

        super(Bullet, self).__init__(bullet_sprite_filename, x=x, y=y, angle=angle, x_speed=x_speed, y_speed=y_speed,
                                     angle_speed=angle_speed)
        self.attack = ship.attack

    def get_damage(self, ship):
        part = get_part(self.sprite.angle, ship.sprite.angle)
        damage = self.attack * (1 - ship.shield[part])
        return damage


def get_part(bullet_angle, ship_angle):
    angle = (bullet_angle - ship_angle) % 360
    if 240 > angle > 120:
        return "front"
    elif angle < 60 or angle > 300:
        return 'rear'
    else:
        return 'side'
