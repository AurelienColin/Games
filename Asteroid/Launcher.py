import sys
import pygame

from Rignak_Games.Sprites import set_scaling_factor


def launch():
    from Rignak_Games.Asteroid.Inputs import manual_input, COMMAND_NUMBER
    from Rignak_Games.Asteroid.GameState import GameState
    game = GameState()

    screenshot, reward, terminal = game.turn([0] * COMMAND_NUMBER)
    while not terminal:
        actions = manual_input()
        screenshot, reward, terminal = game.turn(actions)
        if terminal:
            pygame.quit()


if __name__ == '__main__':
    pygame.init()

    if len(sys.argv) == 2:
        set_scaling_factor(float(sys.argv[1]))
    launcher = launch()
