import math

from Rignak_Games.Sprites import Sprite


class Entity:
    def __init__(self, sprite_filename, x=0, y=0, angle=0, x_speed=0, y_speed=0, angle_speed=0):
        self.x_speed = x_speed
        self.y_speed = y_speed
        self.angle_speed = angle_speed

        self.sprite = Sprite(sprite_filename, x, y, angle)

    def get_movement_angle(self):
        return math.atan(-self.y_speed / self.x_speed) / math.pi * 180

    def pass_turn(self):
        self.sprite.x += self.x_speed
        self.sprite.y += self.y_speed
        self.sprite.angle = (self.sprite.angle + self.angle_speed) % 360
        self.sprite.move(self.sprite.x, self.sprite.y, self.sprite.angle)