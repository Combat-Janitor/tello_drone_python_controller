#!/usr/bin/env python3
# This is a module to display the battery indicator overlay
# on the Tello drone's video feed.

import logging
import time
import pygame

logger = logging.getLogger(__name__)

# ==========================================
# Constants
# ==========================================
# Seconds between battery queries (UDP round-trip)
POLL_INTERVAL = 5
# Battery remapping: raw 90-10% → display 100-0%
RAW_MAX = 90  # Raw % considered "full"
RAW_MIN = 10  # Raw % where auto-land kicks in

# ==========================================
# Module State
# ==========================================
font = None
battery_level = 0
last_poll_time = 0


def init(drone):
    """Initialize the battery indicator.

    Creates the font and takes the first battery reading
    so there's a value to display on the very first frame.

    Args:
        drone: A connected Tello drone instance.
    """
    global font, battery_level, last_poll_time

    # Create the font once (expensive to recreate each frame)
    font = pygame.font.SysFont("Arial", 28, bold=True)

    # Get initial reading before the first poll interval
    battery_level = drone.get_battery()
    last_poll_time = time.time()
    logger.info("Battery module initialized: %s%%", battery_level)


def _remap(raw):
    """Remap raw battery to usable display percentage.

    - >=90% raw  → 100% (full charge)
    - 90% to 10% → 100% to 0% (linear remap)
    - <=10% raw  → returns negative value as a signal
      that we're in the danger zone. The caller
      uses abs() to get the true raw reading.
    """
    if raw >= RAW_MAX:
        return 100
    if raw <= RAW_MIN:
        # Negative = danger zone flag
        return -raw
    # Linear remap across the usable range
    usable_range = RAW_MAX - RAW_MIN
    return int((raw - RAW_MIN) / usable_range * 100)


def draw(screen, drone):
    """Poll the battery (if due) and render the overlay.

    Call this once per frame after blitting the video feed
    but before pygame.display.flip().

    Args:
        screen: The pygame display surface.
        drone: A connected Tello drone instance.
    """
    global battery_level, last_poll_time

    # Only query the drone every few seconds (UDP round-trip)
    if time.time() - last_poll_time > POLL_INTERVAL:
        battery_level = drone.get_battery()
        logger.debug("Raw battery: %s%%", battery_level)
        last_poll_time = time.time()

    # Remap raw battery to usable display range
    display_level = _remap(battery_level)

    # Danger zone: below auto-land threshold
    if display_level < 0:
        # Show real raw value, blinking red
        show_raw = abs(display_level)
        bat_color = (255, 50, 50)  # Red
        # Blink: hide text every other half-second
        blink_on = int(time.time() * 2) % 2 == 0
        label = f"BATTERY: {show_raw}%" if blink_on else ""
    else:
        # Normal display with remapped value
        if display_level > 50:
            bat_color = (0, 220, 80)  # Green
        elif display_level > 20:
            bat_color = (255, 200, 0)  # Yellow
        else:
            bat_color = (255, 50, 50)  # Red
        label = f"Battery: {display_level}%"

    # Render the text surface (True = anti-aliased)
    bat_text = font.render(label, True, bat_color)
    # Draw a semi-transparent background for readability
    bg_rect = bat_text.get_rect()
    bg_rect.topleft = (15, 12)  # Position: top-left corner
    bg_surface = pygame.Surface((bg_rect.width + 16, bg_rect.height + 8))
    bg_surface.set_alpha(140)  # Semi-transparent
    bg_surface.fill((0, 0, 0))  # Black background
    screen.blit(bg_surface, (bg_rect.x - 8, bg_rect.y - 4))
    screen.blit(bat_text, bg_rect)
