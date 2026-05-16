#!/usr/bin/env python3
# This is a module to control the Tello drone using the keyboard


import pygame


def init():
    pygame.init()
    pygame.display.set_mode((1080, 720))
    pygame.display.set_caption("Tello Drone Controller")


def get_key(key_name):
    ans = False
    key_input = pygame.key.get_pressed()
    my_key = getattr(pygame, "K_{}".format(key_name))
    if key_input[my_key]:
        ans = True
    return ans


def update():
    # Process events so input state stays fresh
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False
    return True


def cleanup():
    pygame.quit()