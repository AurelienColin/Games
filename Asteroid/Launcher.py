import sys
import pygame

from Rignak_Games.Sprites import set_scaling_factor

COMMAND_NUMBER = 5


def launch_manual(command_number):
    from Rignak_Games.Asteroid.Inputs import manual_input
    from Rignak_Games.Asteroid.GameState import GameState
    game = GameState()

    screenshot, reward, terminal = game.turn([0] * command_number)
    while not terminal:
        actions = manual_input()
        screenshot, reward, terminal = game.turn(actions)
        if terminal:
            pygame.quit()


def parse_input(argvs):
    if len(argvs) == 1 or argvs[1] == 'manual':
        launcher = launch_manual
    else:
        from Rignak_DeepLearning.Reinforcement import RL
        launcher = RL.Launch
    if len(argvs) == 3:
        set_scaling_factor(float(argvs[2]))
    return launcher


if __name__ == '__main__':
    pygame.init()

    launcher = parse_input(sys.argv)(COMMAND_NUMBER)
