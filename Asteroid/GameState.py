import os

import pygame

from Rignak_Misc.path import get_local_file
from Rignak_Games.Asteroid.Screen import Screen
from Rignak_Games.Asteroid.collisions import get_bullet_collisions, get_ship_collisions
from Rignak_Games.Sprites import SCALING_FACTOR

DEFAULT_BATTLE = 'default'
BATTLE_FILENAME = get_local_file(__file__, os.path.join('res', 'json', 'battles.json'))

SCREEN_WIDTH = 512
SCREEN_HEIGHT = 512

SPRITE_ROOT = os.path.join('res', 'img')
BACKGROUND_FILENAME = get_local_file(__file__, os.path.join(SPRITE_ROOT, 'bg_main.png'))

BACKGROUND = pygame.transform.scale(pygame.image.load(BACKGROUND_FILENAME),
                                    (int(SCREEN_WIDTH * SCALING_FACTOR), int(SCREEN_HEIGHT * SCALING_FACTOR)))

FPS = 20
DAMAGE_ON_COLLISION = 1000


class GameState:
    def __init__(self, battle=DEFAULT_BATTLE, battle_filename=BATTLE_FILENAME, screen_width=SCREEN_WIDTH,
                 screen_height=SCREEN_HEIGHT, background=BACKGROUND, clear=True):
        if clear:
            self.screen = Screen((screen_width, screen_height), background=background)

        self.screen.refresh(None)
        self.screen.initiate_battle(battle, battle_filename)
        self.player = self.screen.ships[0]
        self.frames = 0

    def turn(self, input_action, fps=FPS, damage_on_collision=DAMAGE_ON_COLLISION):
        pygame.event.pump()

        current_player_score = self.player.score

        self.player.use_motor(input_action)
        if input_action[4]:
            self.player.fire()

        bullet_collisions = get_bullet_collisions(self.screen.ships)
        for firing_ship, ship, bullet in bullet_collisions:
            damage = bullet.get_damage(ship)
            reward = ship.receive_damage(damage)
            firing_ship.score += reward

        ship_collisions = get_ship_collisions(self.screen.ships)
        for ship_a, ship_b in ship_collisions:  # each ship will appear as ship_a AND ship_b
            print(ship_a, ship_b)
            ship_a.receive_damage(damage_on_collision)

        for ship in self.screen.ships:
            ship.pass_turn()
        self.screen.trim()

        reward = self.player.score - current_player_score

        self.screen.repop()
        self.screen.refresh(fps)
        screenshot = pygame.surfarray.array2d(self.screen.display)
        self.frames += 1
        if self.player.dead:
            frames = self.frames
            return screenshot, reward, frames
        else:
            return screenshot, reward, False
