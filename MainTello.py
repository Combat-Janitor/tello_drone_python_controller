#!/usr/bin/env python3
# This is the main file to control the Tello drone


import logging
import os
import time

import cv2
from djitellopy import tello

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


def get_keyboard_input(drone, img):
    """Read keyboard state and return RC control values.

    Returns a list of [lr, fb, ud, yv] velocities.
    """
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
        time.sleep(3)
    if kp.get_key("e"):
        logger.info("Taking off...")
        drone.takeoff()

    # Screen capture images from camera
    if kp.get_key("z"):
        os.makedirs(SCREENSHOT_DIR, exist_ok=True)
        filepath = f"{SCREENSHOT_DIR}/{time.time()}.jpg"
        cv2.imwrite(filepath, img)
        logger.info("Screenshot saved: %s", filepath)
        time.sleep(0.3)

    # Return values that are given
    return [lr, fb, ud, yv]


def main():
    global img

    # Initialize Keyboard Input
    kp.init()

    # Connect to the Tello Drone
    drone = tello.Tello()

    try:
        drone.connect()
        logger.info("Battery: %s%%", drone.get_battery())

        # Start the drone camera display stream
        drone.streamon()

        while True:
            # Get return values and store them within variables
            key_values = get_keyboard_input(drone, img)

            # Check for window close
            if not kp.update():
                logger.info("Window closed, shutting down...")
                break

            # Control the Tello drone
            drone.send_rc_control(
                key_values[0], key_values[1], key_values[2], key_values[3]
            )

            # Get Frames from the Tello drone camera
            img = drone.get_frame_read().frame
            img = cv2.resize(img, (1080, 720))

            # Show the frames on PC display
            cv2.imshow("DroneCapture", img)
            cv2.waitKey(1)

    except KeyboardInterrupt:
        logger.info("Interrupted by user, shutting down...")
    except Exception as e:
        logger.error("Unexpected error: %s", e)
    finally:
        logger.info("Landing drone and cleaning up...")
        try:
            drone.land()
        except Exception:
            pass
        try:
            drone.streamoff()
        except Exception:
            pass
        cv2.destroyAllWindows()
        kp.cleanup()


if __name__ == "__main__":
    main()
