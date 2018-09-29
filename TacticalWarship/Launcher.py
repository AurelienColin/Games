# -*- coding: utf-8 -*-
"""
Created on Thu Jul  5 18:00:07 2018

@author: Rignak
"""
from TacticalWarship import Screen
import sys
import pygame
import random
from pygame.locals import KEYDOWN, K_RETURN, QUIT, K_UP, K_DOWN, K_LEFT, K_RIGHT
from PIL import Image

from os.path import join
# ------------------------------
# place for global constants
learning = True
battle = 'staticTower'

FACTOR = 0.5
SCREENWIDTH  = int(512*FACTOR)
SCREENHEIGHT = int(512*FACTOR)
pygame.init()
background = pygame.transform.scale(pygame.image.load(join('res', 'img', 'bg_main.png')),
                                    (SCREENWIDTH, SCREENHEIGHT))
# ------------------------------

class GameState:
    def __init__(self, clear=True):
        if clear:
            self.screen = Screen.Screen((SCREENWIDTH, SCREENHEIGHT), background, FACTOR=FACTOR)
        else:
            self.screen.ships = []
            self.screen.p = 1
        self.screen.Refresh(None)
        self.screen.InitiateBattle(battleType = battle)
        self.player = self.screen.ships[0]
        self.frames = 0

    def FrameStep(self, inputAction, FPS=30):
        pygame.event.pump()

        reward = 0
        self.player.Motor(inputAction)
        if inputAction[6] == 1:
            self.player.scorePlayer += self.player.Fire()*5
            #reward -= 0.01

        self.screen.MoveSprites()
        collisions = self.screen.GetBulletCollisions()
        for ship1, ship2, bullet in collisions:
            dmg = GetBulletDamage(ship1[0], ship2[0], bullet[0])
            self.screen.ships[ship2[1]].ApplyDamage(dmg)
            #reward += 0.1

        collisions = self.screen.GetShipCollisions()
        for ship1, ship2 in collisions:
            self.screen.ships[ship2[1]].ApplyDamage(1000)

        if battle == 'staticTower':
            self.screen.Repop()
        self.screen.Refresh(FPS)
        self.frames += 1

        imageData = pygame.surfarray.array2d(self.screen.display)

        if self.player.killedInDuty == True:
            reward -= 1
            frames = self.frames
            self.__init__(clear=False)
            return imageData, reward, frames
        else:
            reward += 0.01
            self.player.scorePlayer += reward
            return imageData, reward, False




def GetBulletDamage(ship1, ship2, bullet):
    part = GetPart(bullet.sprite.angle, ship2.sprite.angle)
    dmg = ship1.damage*(1-ship2.shield[part])
    return dmg

def GetPart(angle1, angle2):
    angle = (angle1-angle2)%360
    if angle > 120 and angle < 240:
        part = "front"
    elif angle <60 or angle > 300:
        part = "rear"
    else:
        part = "side"
    return part

def ManualInput():
    for event in pygame.event.get():
        if event.type == QUIT:  # The game is closed
            pygame.quit()
            sys.exit()
    keys = pygame.key.get_pressed()
    actions = [0, 0, 0, 0, 0, 0, 0, 0]
    if keys[K_UP]:
        actions[0] = 1
    elif keys[K_DOWN]:
        actions[1] = 1
    else:
        actions[2] = 1
    if keys[K_RIGHT]:
        actions[4] = 1
    elif keys[K_LEFT]:
        actions[3] = 1
    else:
        actions[5] = 1
    if keys[K_RETURN]:
        actions[6] = 1
    else:
        actions[7] = 1
    return actions

def LaunchManual():
    game = GameState()
    xT, r0, terminal = game.FrameStep([0, 0, 1, 0, 0, 1, 0, 1])
    while not terminal:
        actions = ManualInput()
        xT, rT, terminal = game.FrameStep(actions)
        if terminal:
            pygame.quit()
            break

def TrainNetwork(model, args):
    from collections import deque
    import numpy as np
    from keras.optimizers import Adam
    imgSizeX, imgSizeY = args['shape'][:2]

    game = GameState()
    D = deque()

    doNothing = [0, 0, 1, 0, 0, 1, 0, 1]
    x0, r0, terminal = game.FrameStep(doNothing, FPS=None)

    x0 = RL.FormatPic(x0, imgSizeX, imgSizeY)
    s0 = np.stack((x0, x0, x0, x0), axis=2)
    s0 = s0.reshape(1, s0.shape[0], s0.shape[1], s0.shape[2])

    if args['mode'] == 'Run':
        OBSERVE = 999999999    #We keep observe, never train
        epsilon = args['final_epsilon']
        print ("Now we load weight")
        model.load_weights("model.h5")
        adam = Adam(lr=args['lr'])
        model.compile(loss='mse',optimizer=adam)
        print ("Weight load successfully")
    else:                       #We go to training mode
        OBSERVE = args['observation']
        epsilon = args['ini_epsilon']

    t = 0

    from datetime import datetime
    d2 = datetime.now()-datetime.now()
    d3 = d2
    d1 = d2
    delta_epsilon = (args['ini_epsilon'] - args['final_epsilon']) / args['exploration']


    rdBatch = args['shape'][2]-1
    batchNb = args['batch']
    replay = args['replay']
    finalE = args['final_epsilon']
    gamma = args['gamma']
    delay = args['delay']
    ACTIONS = 8
    model.plot = RL.Plot()
    cumR = 0
    loss_mean = 0
    Qsa_maxmean = 0
    exp = 0
    frames = []
    begin = datetime.now()
    while (True):
        a0 = np.zeros([ACTIONS])
        r0 = 0
        if args['mode'] == 'Run' :
            q = model.predict(s0)[0]
            act_i = np.argmax(q)
            FPS = 30
        elif t < OBSERVE and manualTrain == True:
            q = ManualInput()
            act_i = np.argmax(q)
            FPS = 30
        elif t < OBSERVE or random.random() < epsilon:  # exploration
            act_i = random.randrange(ACTIONS)
            FPS = None
        else:
            q = model.predict(s0)[0]
            act_i = np.argmax(q)
            exp += q[act_i]
            FPS = None
        a0[act_i] = 1

        if epsilon > finalE and t > OBSERVE:
            epsilon -= delta_epsilon

        begin1 = datetime.now()
        x1, r0, terminal = game.FrameStep(a0, FPS=FPS)
        for i in range(args['frameSkip']):
            game.FrameStep(doNothing, FPS=FPS)
        d1 +=  datetime.now() - begin1

        if terminal:
            frames.append(terminal)
            terminal = True

        cumR += r0
        x1 = RL.FormatPic(x1, imgSizeX, imgSizeY)
#        if t == 1000:
#            return
#        im = Image.fromarray(x1*255)
#        im = im.convert('RGB')
#        im.save(f"im\\{t}.jpeg")
        x1 = x1.reshape(1, imgSizeX, imgSizeY, 1)
        s1 = np.append(x1, s0[:, :, :, :rdBatch], axis=3)
        D.append((s0, s1, act_i, r0, terminal))


        if len(D) > replay:
            D.popleft()
        if t > OBSERVE:
            begin2 = datetime.now()
            targets, input_, maxQ_sa = RL.UpdateRule(D, batchNb, model, gamma)
            d2 +=  datetime.now() - begin2

            begin3 = datetime.now()
            loss_mean += model.train_on_batch(input_, targets)
            d3 +=  datetime.now() - begin3
            Qsa_maxmean += max(maxQ_sa)

        if t % delay == 0 and t:
            cumR /= delay
            frames  = np.mean(frames)
            if t <= OBSERVE:
                Qsa_maxmean = None
                loss_mean = None
                exp = None
            else:
                Qsa_maxmean /= delay
                loss_mean /= delay
                exp /= delay
                if len(model.plot.rewards)>OBSERVE//delay:
                    m = max(model.plot.rewards[OBSERVE//delay:])
                else:
                    m = -1
                print(f'{t} - [{round(cumR, 5)}|{round(m, 5)}] - e: [{round(epsilon,4)}]')
#                if cumR >= m:
#                    print('Model get more rewards than before, we save the weights')
#                    model.save_weights("model.h5", overwrite=True)
#                    with open("model.json", "w") as outfile:
#                        json.dump(model.to_json(), outfile)
#                else:
#                    print('Model get less rewards than before, we rollback')
#                    model.load_weights("model.h5")
#                    adam = Adam(lr=args['lr'])
#                    model.compile(loss='mse',optimizer=adam)
            model.plot.Plot(Qsa_maxmean, loss_mean, cumR, exp, frames,
                            [d1, (datetime.now()-begin)-d3-d2-d1, d2, d3], t, OBSERVE)
            cumR = 0
            Qsa_maxmean = 0
            loss_mean = 0
            exp = 0
            frames = []

        s0 = s1
        t += 1



def LaunchRL():
    args = {}
    args['actF'] =              'relu'
    args['lr'] =                10**-4
    args['shape'] =             (84, 84, 4)
    args['final_epsilon'] =     10**-2
    args['ini_epsilon'] =       1
    args['observation'] =       10000
    args['exploration'] =       230000
    args['batch'] =             32
    args['gamma'] =             0.99
    args['replay'] =            30000
    args['observation'] =       10000
    args['frameSkip'] =         0
    args['delay'] =             2500
    args['mode'] =              "Train"

    model = RL.BuildModel(args)
    RL.ExportSummary(model)
    TrainNetwork(model,args)

learning = True
continueTraining = False
manualTrain = False
if __name__ == '__main__':
    if not learning:
        LaunchManual()
    else:
        from TacticalWarship import RL
        import tensorflow as tf
        config = tf.ConfigProto()
        config.gpu_options.allow_growth = True
        sess = tf.Session(config=config)
        from keras import backend as K
        K.set_session(sess)
        LaunchRL()