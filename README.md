# Tello Drone Controller

A Python-based application to control a DJI Tello drone using your PC keyboard. This project allows you to fly the drone, view its live camera feed, and capture photos using simple keyboard inputs.

## Features

- **Full Flight Control:** Use intuitive keyboard bindings to control altitude, translation, and rotation.
- **Live Video Feed:** Streams the drone's 720p camera feed directly to your PC using OpenCV.
- **Photo Capture:** Snap photos mid-flight with a single keystroke (directories are auto-created).
- **Graceful Shutdown:** Automatically lands the drone and safely closes video streams if the window is closed or interrupted.
- **Console Logging:** Built-in logging provides real-time feedback on battery life, flight status, and errors.
- **Modular Design:** PyGame keyboard logic is separated from the main flight logic for easier maintenance.

## Requirements

You will need Python 3 installed on your system. **Note:** This project cannot easily be run inside a Docker container because it requires direct access to your host's display (for the PyGame and OpenCV windows) and direct WiFi access to communicate with the drone. You must run this locally using a Python virtual environment.

### Setup Instructions

1. **Install System Dependencies (macOS only):**
If you are on a Mac, you may need to install SDL2 dependencies before installing the Python packages, otherwise PyGame will fail to install:
```bash
brew install sdl2 sdl2_image sdl2_ttf sdl2_mixer
```

2. **Create a virtual environment (from the root of your project):**
```bash
python3 -m venv venv
```

3. **Activate the virtual environment:**
- On macOS/Linux: `source venv/bin/activate`
- On Windows: `venv\Scripts\activate`

4. **Install the Python dependencies:**
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

> **macOS Note:** You may see a wall of `objc` warnings about duplicate SDL2 classes. These are harmless warnings caused by both PyGame and OpenCV bundling their own copies of SDL2. They will not affect functionality. To suppress them, run with:
> ```bash
> OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES python MainTello.py 2>/dev/null
> ```

4. A PyGame window and an OpenCV video stream window will appear. **Make sure the PyGame window is actively selected/in-focus** so it can register your keystrokes.

## Flight Controls

| Key | Action |
| :--- | :--- |
| **E** | Takeoff |
| **Q** | Land |
| **W / S** | Up / Down |
| **UP / DOWN** | Forward / Backward |
| **LEFT / RIGHT** | Fly Left / Fly Right |
| **A / D** | Rotate (Yaw) Left / Rotate (Yaw) Right |
| **Z** | Capture Photo (saves to `tellopy/Resources/Images/`) |

## Project Structure

- `MainTello.py`: The core script that handles the connection to the drone, routes keyboard inputs to movement commands, and manages the OpenCV video stream.
- `KeyboardTelloModule.py`: A helper module that initializes a PyGame window and handles all keyboard event polling safely.
