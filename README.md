# Tello Drone Controller

A Python-based application to control a DJI Tello drone using your PC keyboard or a PS5 DualSense controller. This project allows you to fly the drone, view its live camera feed, and capture photos using simple inputs.

## Features

- **Full Flight Control:** Use intuitive keyboard bindings to control altitude, translation, and rotation.
- **Live Video Feed:** Streams the drone's 720p camera feed directly to your PC using OpenCV.
- **Photo Capture:** Snap photos mid-flight with a single keystroke (non-blocking 0.3s cooldown ensures controls never freeze).
- **Smart Graceful Shutdown:** Automatically lands the drone only if it's currently flying, and safely closes video streams on exit.
- **Battery Indicator:** A color-coded battery overlay on the video feed — green (>50%), yellow (20–50%), red (<20%) — polled every 5 seconds.
- **Console Logging:** Built-in logging provides real-time feedback on battery life, flight status, and errors.
- **Modular Design:** Input modules are organized in a `modules/` package, separated from the main flight logic for easier maintenance.
- **PS5 Controller Support:** Plug in a DualSense controller for proportional analog stick control with automatic detection and keyboard fallback.

## Requirements

You will need Python 3 installed on your system. **Note:** This project cannot easily be run inside a Docker container because it requires direct access to your host's display (for the PyGame and OpenCV windows) and direct WiFi access to communicate with the drone. You must run this locally using a Python virtual environment.

### Setup Instructions

1. **Install System Dependencies (macOS only):**
If you are on a Mac, you may need to install SDL2 dependencies before installing the Python packages, otherwise PyGame will fail to install:

```bash
brew install sdl2 sdl2_image sdl2_ttf sdl2_mixer
```

1. **Create a virtual environment (from the root of your project):**

```bash
python3 -m venv venv
```

1. **Activate the virtual environment:**

- On macOS/Linux: `source venv/bin/activate`
- On Windows: `venv\Scripts\activate`

1. **Install the Python dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

## How to Use

1. Turn on your Tello drone.
2. Connect your PC to the drone's WiFi network (usually named something like `TELLO-XXXXXX`).
3. Run the main application script:

```bash
python MainTello.py
```

> **macOS Note:** You may see `objc` warnings about duplicate SDL2 classes in the terminal. These are cosmetic warnings from OpenCV's bundled SDL2 and will not affect functionality. To suppress them, run with:
>
> ```bash
> python MainTello.py 2>/dev/null
> ```

1. A single PyGame window will appear showing the drone's camera feed. **Make sure this window is in focus** so it can register your inputs.

## Flight Controls

| Key | Action |
| :--- | :--- |
| **E** | Takeoff |
| **Q** | Land (press again after landing to exit the program) |
| **W / S** | Up / Down |
| **UP / DOWN** | Forward / Backward |
| **LEFT / RIGHT** | Fly Left / Fly Right |
| **A / D** | Rotate (Yaw) Left / Rotate (Yaw) Right |
| **Z** | Capture Photo (saves to `tellopy/Resources/Images/`) |

## Controller Support (PS5 DualSense)

If a PS5 DualSense controller is connected (USB or Bluetooth) before launching the app, it will be auto-detected and used instead of keyboard input. If no controller is found, the app falls back to keyboard controls.

**Analog sticks provide proportional speed control** — gentle tilts produce slow movement, full tilts produce maximum speed. This is a significant upgrade over the binary on/off keyboard input.

| Input | Action |
| :--- | :--- |
| **Left Stick** | Move (Left/Right + Forward/Back) |
| **Right Stick** | Altitude (Up/Down) + Yaw Rotation |
| **△ Triangle** | Takeoff |
| **✕ Cross** | Land (press again after landing to exit) |
| **○ Circle** | Capture Photo |

> **Note:** Button mappings are configured per-OS via `platform.system()` in `modules/ControllerTelloModule.py`. If your controller's buttons don't match, update the `MAPPINGS` dictionary in that file.

## Battery Indicator

The battery level is displayed in the top-left corner of the video feed. The raw battery percentage from the drone is **remapped to a usable display range** so the numbers are more intuitive:

| Raw Battery (from drone) | Display | Behavior |
| :--- | :--- | :--- |
| ≥90% | **100%** | Green — full charge |
| 90% → 10% | **100% → 0%** | Green / Yellow / Red as it drains |
| ≤10% | **Blinking red** (shows raw %) | Danger zone — drone will attempt to auto-land |

**Why remap?** A freshly charged Tello battery typically reports 90–93%, never a true 100%. The display remaps this so a full charge reads as 100% and drains smoothly to 0%. Below 10%, the indicator switches to a blinking red warning showing the actual raw value — the drone is trying to auto-land at this point, but you can still force it to fly.

**Note:** The battery percentage drops quickly at first (100→60% displayed), then levels off for most of your flight time. This is standard LiPo battery discharge behavior, not a bug.

## Project Structure

- `MainTello.py`: The core script that connects to the drone, routes input to movement commands, and renders the video stream.
- `modules/`: Module package.
  - `BatteryTelloModule.py`: Battery indicator overlay with remapped display range and blinking danger zone alert.
  - `KeyboardTelloModule.py`: Initializes the PyGame window and handles keyboard event polling.
  - `ControllerTelloModule.py`: PS5 DualSense controller support with OS-agnostic button/axis mapping and analog dead zone filtering.
