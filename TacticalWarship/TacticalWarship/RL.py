# -*- coding: utf-8 -*-
"""
Created on Sat Sep 15 11:05:05 2018

@author: Rignak
"""
from keras.models import Model
from keras.layers.core import Dense#, Dropout, Flatten
#from keras.layers import concatenate
from keras.layers import Input
#from keras.layers.convolutional import Convolution2D, MaxPooling2D, Conv3D, MaxPooling3D
from keras.optimizers import SGD, Adam
import skimage as skimage
#from skimage import transform, exposure
import numpy as np
import sys
import random
import matplotlib.pyplot as plt
import cv2

def BuildModel(args):
    shape = args['shape']
    actF = args['actF']

    I1 = Input(shape=shape)
#    x1 = Convolution2D(64, 8, strides=(2, 2), activation=actF, padding='same')(I1)
#    x1 = MaxPooling2D((2, 2), strides=(2, 2))(x1)
#    x1 = Convolution2D(128, 4, strides=(2, 2), activation=actF, padding='same')(x1)
#    x1 = MaxPooling2D((2, 2), strides=(2, 2))(x1)
#    x1 = Convolution2D(256, 3, strides=(2, 2), activation=actF, padding='same')(x1)
#    x1 = MaxPooling2D((2, 2), strides=(2, 2))(x1)
#    x1 = Flatten()(x1)
#    x1 = Dense(512, activation=actF)(x1)
    x1 = Dense(64, activation='selu')(I1)
    x1 = Dense(32, activation='selu')(I1)
    x1 = Dense(16, activation='selu')(I1)
    x1 = Dense(8, activation='linear')(x1)

    model = Model(inputs=[I1], outputs=[x1])
    print(model.summary())
    sgd = SGD(lr=args['lr'],momentum=0.5, nesterov=True)
    adam = Adam(lr=args['lr'])
    model.compile(loss='mse',optimizer=adam)
    print('BuildModel OK')
    return model

def UpdateRule(D, batchNb, model, gamma):
    batch = random.sample(D, batchNb)
    s0, s1, act_i, reward_t, terminal = zip(*batch)
    s0 = np.concatenate(s0)
    s1 = np.concatenate(s1)
    targets = model.predict(s0)
    Q_sa = model.predict(s1)
    maxQ_sa = np.mean(Q_sa, axis=1)
    targets[range(batchNb), act_i] = reward_t + gamma*maxQ_sa*np.invert(terminal)
    targets = np.clip(targets, -1, 1)
    return targets, s0, maxQ_sa

def FormatPic(x_t, imgSizeX, imgSizeY):
    x_t = skimage.color.rgb2gray(x_t)
    x_t = skimage.transform.resize(x_t,[imgSizeX, imgSizeY])
    x_t = skimage.exposure.rescale_intensity(x_t,out_range=(0,1))
    return x_t


def ExportSummary(model):
    old = sys.stdout
    with open('currentModel.txt', 'w') as file:
        sys.stdout = file
        model.summary()
        sys.stdout = old


def GetMap(SCREENWIDTH, SCREENHEIGHT, state, model):
    f=5
    SCREENWIDTH = SCREENWIDTH//f
    SCREENHEIGHT= SCREENHEIGHT//f

    cStates = np.zeros((SCREENWIDTH*SCREENHEIGHT,66))
    cStates[:,] = state[0]
    for i in range(SCREENWIDTH):
        for j in range(SCREENHEIGHT):
            cStates[i*SCREENWIDTH+j,0] = (i-SCREENWIDTH/2)/2*f
            cStates[i*SCREENWIDTH+j,1] = (j-SCREENHEIGHT/2)/2*f
            #cStates[i*SCREENWIDTH+j,2:]= state[2:]
    mapping = model.predict(cStates)
    mapping = mapping.reshape((SCREENWIDTH, SCREENHEIGHT, 8))
    mapping[0,0] = 0
    cv2.imshow('pos', mapping[:,:,2])


class Plot():
    def __init__(self):
       self.maxQs = []
       self.losss = []
       self.frames = []
       self.rewards = []
       self.survivals = []
       self.expected = []


    def Plot(self, maxQ, loss, r, exp, survival, frame, OBSERVE):
        plt.ioff()
        plt.clf()
        self.maxQs.append(maxQ)
        self.losss.append(loss)
        self.rewards.append(r)
        self.survivals.append(survival)
        self.expected.append(exp)
        self.frames.append(frame)

        # plot maxQ
        plt.subplot(3,2,1)
        plt.plot(self.frames, self.maxQs)
        plt.xlabel('frame')
        plt.ylabel('maxQ')

        # plot loss
        plt.subplot(3,2,2)
        plt.yscale('log')
        plt.plot(self.frames, self.losss)
        plt.xlabel('frame')
        plt.ylabel('loss')

        # plot rewards
        plt.subplot(3,2,3)
        plt.plot(self.frames, self.rewards)
        plt.xlabel('frame')
        plt.ylabel('mean reward')

        # plot rewards
        plt.subplot(3,2,4)
        plt.plot(self.frames, self.survivals)
        plt.xlabel('frame')
        plt.ylabel('mean survival')

        # plot expected reward
        plt.subplot(3,2,5)
        plt.plot(self.frames, self.expected)
        plt.xlabel('frame')
        plt.ylabel('expected reward')

        plt.tight_layout()
        plt.savefig('plot.png')

        plt.draw()