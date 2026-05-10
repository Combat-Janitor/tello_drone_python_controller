#!/usr/bin/env python3

# This is a module to control the Tello drone using the keyboard

import pygame

def init():
    pygame.init()
    window = pygame.display.set_mode((400, 400))

def getKey(keyName):
    ans = False
    keyInput = pygame.key.get_pressed()
    myKey = getattr(pygame, 'K_{}'.format(keyName))
    if keyInput[myKey]:
        ans = True
    return ans

def update():
    # Process events and update display once per frame
    for event in pygame.event.get():
        pass
    pygame.display.update()

