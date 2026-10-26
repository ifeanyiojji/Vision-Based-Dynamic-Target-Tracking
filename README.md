# Vision-Based Dynamic Target Tracking and Visual Servoing

A small, runnable implementation of a MobileAerial-style vision loop:

1. Select or initialize a moving target in the camera image.
2. Track its bounding box frame by frame with OpenCV.
3. Convert image-centering and apparent-size errors into bounded, normalized
   image-based visual-servo requests.

The project runs in a synthetic camera-free demo, from a webcam, or on a video
file. The generated commands are for visualization and experimentation only;
they are **not** connected to a flight controller and must not be sent directly
to an aircraft.

## Requirements

- Python 3.10+
- OpenCV contrib and NumPy (listed in `requirements.txt`)
- A display for the interactive OpenCV window

## Setup

From this folder in PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
```

## Run

Start the synthetic moving-target scene (default):

```powershell
.\.venv\Scripts\python -m mobileaerial.app
```

Run from a webcam (the first camera is index `0`):

```powershell
.\.venv\Scripts\python -m mobileaerial.app --source 0
```

Or use a video file:

```powershell
.\.venv\Scripts\python -m mobileaerial.app --source "C:\path\to\video.mp4"
```

When using a camera or video, drag a rectangle around the target and press
Enter or Space to confirm. Press `r` to reselect after initialization, or `q`
or Escape to quit. The synthetic demo initializes on its built-in target.

## Controller convention

The controller uses normalized target-center errors and the logarithm of the
desired-to-observed target-width ratio. It outputs three bounded requests:

- `lateral`: move right when the target is right of image center
- `vertical`: move up when the target is below image center
- `forward`: move closer when the target appears smaller than the desired size

Signs describe camera-motion requests under a forward-facing pinhole camera.
They are deliberately not calibrated physical velocities. The default target
width is 22% of the image width; proportional gains and command saturation are
in `ServoConfig`.

## Tests

```powershell
.\.venv\Scripts\python -m unittest discover -s tests -v
```

The unit tests cover centering, apparent-size regulation, command saturation,
and invalid controller inputs. The OpenCV tracker uses CSRT when available,
then falls back to KCF or MOSSE.
