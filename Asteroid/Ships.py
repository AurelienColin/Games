import math
import os
import json
from functools import lru_cache

from Rignak_Games.Entities import Entity
from Rignak_Games.Asteroid.Bullets import Bullet

from Rignak_Misc.path import get_local_file

SHIP_FILENAME = get_local_file(__file__, os.path.join('res', 'json', 'ships.json'))


class Ship(Entity):
    def __init__(self, ship_name, team, x, y, angle, x_speed=0, y_speed=0, angle_speed=0, ship_filename=SHIP_FILENAME):
        ship = load(ship_name, ship_filename=ship_filename)
        super(Ship, self).__init__(ship['sprite'], x=x, y=y, angle=angle,
                                   x_speed=x_speed, y_speed=y_speed, angle_speed=angle_speed)
        self.team = team
        self.dead = False
        self.score = 0
        self.bullet_sprite = ship['bullet_sprite']

        self.reward = ship['reward']
        self.hp = ship['hp']
        self.shield = ship['shield']

        self.acceleration = ship['acceleration']

        self.bullets = []
        self.fire_delay = ship['fire_delay']
        self.last_fire = 0
        self.attack = ship['attack']
        self.bullet_speed = ship['bullet_speed']

    def use_motor(self, command):
        """
        0 : forward
        1 : backward
        2 : left
        3 : right
        """

        if command[0]:
            acceleration_rate = self.acceleration['front']
        elif command[1]:
            acceleration_rate = -self.acceleration['rear']
        else:
            acceleration_rate = 0

        if command[2]:
            self.angle_speed -= self.acceleration['side']
        elif command[3]:
            self.angle_speed += self.acceleration['side']

        angle = self.sprite.angle / 180 * math.pi
        self.x_speed += acceleration_rate * math.cos(angle)
        self.y_speed -= acceleration_rate * math.sin(angle)

    def fire(self):
        if self.last_fire > self.fire_delay:
            self.bullets.append(Bullet(self, self.bullet_sprite))
            self.score += self.reward['on_fire']

    def receive_damage(self, damage):
        reward = min(self.hp, damage) * self.reward['on_damage']
        self.hp -= damage
        if self.hp <= 0:
            reward += self.kill()
        return reward

    def kill(self):
        self.dead = True
        reward = self.reward['on_death']
        self.score -= self.reward['on_death']
        return reward

    def pass_turn(self):
        super().pass_turn()
        self.last_fire += 1
        for bullet in self.bullets:
            bullet.pass_turn()


@lru_cache(maxsize=1)
def load(ship_name, ship_filename=SHIP_FILENAME):
    with open(ship_filename, 'r') as battle_file:
        ships = json.load(battle_file)
    return ships[ship_name]
