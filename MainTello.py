#!/usr/bin/env python3
# This is the main file to control the Tello drone


import logging
import os
import time
import cv2
import pygame
from djitellopy import tello
import ControllerTelloModule as cp
import KeyboardTelloModule as kp

# ==========================================
# Constants
# ==========================================
SPEED = 80
LIFT_SPEED = 80
MOVE_SPEED = 85
ROTATION_SPEED = 100
SCREENSHOT_DIR = "tellopy/Resources/Images"

# ==========================================
# Logging Configuration
# ==========================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

img = None
last_photo_time = 0
use_controller = False


def get_keyboard_input(drone, img):
    """Read keyboard state and return RC control values.

    Returns a list of [lr, fb, ud, yv] velocities.
    """
    global last_photo_time
    # LEFT RIGHT, FRONT BACK, UP DOWN, YAW VELOCITY
    lr, fb, ud, yv = 0, 0, 0, 0

    # Controls for the Left and Right movements
    if kp.get_key("LEFT"):
        lr = -SPEED
    elif kp.get_key("RIGHT"):
        lr = SPEED

    # Controls for the Front and Back movements
    if kp.get_key("UP"):
        fb = MOVE_SPEED
    elif kp.get_key("DOWN"):
        fb = -MOVE_SPEED

    # Controls for the Up and Down movements
    if kp.get_key("w"):
        ud = LIFT_SPEED
    elif kp.get_key("s"):
        ud = -LIFT_SPEED

    # Controls for drone rotation movements
    if kp.get_key("d"):
        yv = ROTATION_SPEED
    elif kp.get_key("a"):
        yv = -ROTATION_SPEED

    # Controls for drone landing and takeoff
    if kp.get_key("q"):
        logger.info("Landing drone...")
        drone.land()
    if kp.get_key("e"):
        logger.info("Taking off...")
        drone.takeoff()

    # Screen capture images from camera (with 0.3s cooldown)
    if kp.get_key("z"):
        if time.time() - last_photo_time > 0.3:
            os.makedirs(SCREENSHOT_DIR, exist_ok=True)
            filepath = f"{SCREENSHOT_DIR}/{time.time()}.jpg"
            cv2.imwrite(filepath, img)
            logger.info("Screenshot saved: %s", filepath)
            last_photo_time = time.time()

    # Return values that are given
    return [lr, fb, ud, yv]


def get_controller_input(drone, img):
    """Read controller state and return RC control values.

    Analog sticks provide proportional speed control (float -1.0 to 1.0
    multiplied by the speed constant), unlike the binary keyboard input.

    Returns a list of [lr, fb, ud, yv] velocities.
    """
    global last_photo_time

    # Analog sticks → proportional movement
    lr = int(cp.get_axis("left_x") * SPEED)
    fb = int(-cp.get_axis("left_y") * MOVE_SPEED)  # Y-axis is inverted
    yv = int(cp.get_axis("right_x") * ROTATION_SPEED)
    ud = int(-cp.get_axis("right_y") * LIFT_SPEED)  # Y-axis is inverted

    # Buttons → discrete actions
    if cp.get_button("cross"):
        logger.info("Landing drone...")
        drone.land()
    if cp.get_button("triangle"):
        logger.info("Taking off...")
        drone.takeoff()

    # Screenshot (with 0.3s cooldown)
    if cp.get_button("circle"):
        if time.time() - last_photo_time > 0.3:
            os.makedirs(SCREENSHOT_DIR, exist_ok=True)
            filepath = f"{SCREENSHOT_DIR}/{time.time()}.jpg"
            cv2.imwrite(filepath, img)
            logger.info("Screenshot saved: %s", filepath)
            last_photo_time = time.time()

    return [lr, fb, ud, yv]


def main():
    global img, use_controller

    # Initialize Keyboard Input
    kp.init()

    # Attempt to initialize controller (falls back to keyboard if not found)
    use_controller = cp.init()
    if use_controller:
        logger.info("Controller mode active — using analog sticks.")
    else:
        logger.info("Keyboard mode active.")

    # Connect to the Tello Drone
    drone = tello.Tello()

    try:
        drone.connect()
        logger.info("Battery: %s%%", drone.get_battery())

        # Start the drone camera display stream
        drone.streamon()

        while True:
            # Pump the event queue first so input state is fresh
            if not kp.update():
                logger.info("Window closed, shutting down...")
                break

            # Get return values from active input method
            if use_controller:
                key_values = get_controller_input(drone, img)
            else:
                key_values = get_keyboard_input(drone, img)

            # Control the Tello drone
            drone.send_rc_control(
                key_values[0], key_values[1], key_values[2], key_values[3]
            )

            # Get Frames from the Tello drone camera
            img = drone.get_frame_read().frame
            img = cv2.resize(img, (1080, 720))

            # Render the camera feed in the pygame window
            # Convert OpenCV BGR frame to RGB for pygame
            frame_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            frame_surface = pygame.image.frombuffer(
                frame_rgb.tobytes(), frame_rgb.shape[1::-1], "RGB"
            )
            screen = pygame.display.get_surface()
            screen.blit(frame_surface, (0, 0))
            pygame.display.flip()

    except KeyboardInterrupt:
        logger.info("Interrupted by user, shutting down...")
    except Exception as e:
        logger.error("Unexpected error: %s", e)
    finally:
        logger.info("Cleaning up...")
        # Only attempt to land if the drone is actually flying
        if getattr(drone, "is_flying", False):
            logger.info("Drone is still flying, landing now...")
            try:
                drone.land()
            except Exception:
                pass
        try:
            drone.streamoff()
        except Exception:
            pass
        cp.cleanup()
        kp.cleanup()


if __name__ == "__main__":
    main()