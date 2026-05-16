#!/usr/bin/env python3
# This is a module to control the Tello drone using a PS5 DualSense controller

import logging
import platform
import pygame

logger = logging.getLogger(__name__)

# ==========================================
# Dead Zone Configuration
# ==========================================
# Analog sticks rarely rest at perfect 0.0. Any value below this
# threshold is treated as zero to prevent unintended drift.
DEAD_ZONE = 0.1

# ==========================================
# OS-Agnostic Button / Axis Mapping
# ==========================================
# DualSense button and axis indices can vary across operating systems.
# Each key maps a logical action to the raw SDL2 index for that platform.

MAPPINGS = {
    "Darwin": {  # macOS
        "axes": {
            "left_x": 0,  # Left stick horizontal  → Left / Right
            "left_y": 1,  # Left stick vertical    → Forward / Back
            "right_x": 2,  # Right stick horizontal → Yaw rotation
            "right_y": 3,  # Right stick vertical   → Up / Down
        },
        "buttons": {
            "cross": 0,  # ✕  → Land
            "circle": 1,  # ○  → Screenshot
            "triangle": 3,  # △  → Takeoff
        },
    },
    "Windows": {
        "axes": {
            "left_x": 0,
            "left_y": 1,
            "right_x": 2,
            "right_y": 3,
        },
        "buttons": {
            "cross": 0,
            "circle": 1,
            "triangle": 3,
        },
    },
    "Linux": {
        "axes": {
            "left_x": 0,
            "left_y": 1,
            "right_x": 2,
            "right_y": 3,
        },
        "buttons": {
            "cross": 0,
            "circle": 1,
            "triangle": 3,
        },
    },
}

# ==========================================
# Module State
# ==========================================
joystick = None
mapping = None


def init():
    """Initialize the joystick subsystem and connect to the first controller.

    Returns True if a controller was detected, False otherwise.
    """
    global joystick, mapping

    pygame.joystick.init()

    if pygame.joystick.get_count() == 0:
        logger.info("No controller detected — falling back to keyboard.")
        return False

    joystick = pygame.joystick.Joystick(0)
    joystick.init()

    # Select the mapping for the current OS
    os_name = platform.system()
    mapping = MAPPINGS.get(os_name, MAPPINGS["Linux"])

    logger.info("Controller connected: %s", joystick.get_name())
    logger.info("Platform detected: %s", os_name)
    return True


def get_axis(axis_name):
    """Return the current value of an analog axis with dead zone applied.

    Args:
        axis_name: One of 'left_x', 'left_y', 'right_x', 'right_y'.

    Returns:
        A float between -1.0 and 1.0, or 0.0 if within the dead zone.
    """
    if joystick is None or mapping is None:
        return 0.0

    axis_id = mapping["axes"].get(axis_name)
    if axis_id is None:
        return 0.0

    value = joystick.get_axis(axis_id)
    if abs(value) < DEAD_ZONE:
        return 0.0
    return value


def get_button(button_name):
    """Return True if the named button is currently pressed.

    Args:
        button_name: One of 'cross', 'circle', 'triangle'.
    """
    if joystick is None or mapping is None:
        return False

    button_id = mapping["buttons"].get(button_name)
    if button_id is None:
        return False

    return joystick.get_button(button_id)


def cleanup():
    """Release the joystick and shut down the subsystem."""
    global joystick
    if joystick is not None:
        joystick.quit()
        joystick = None
    pygame.joystick.quit()
