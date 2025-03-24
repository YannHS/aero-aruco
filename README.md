# Aero uOttawa companion computer for Ardupilot
This code repository is intended to be run on a Raspberry pi CM4 on the Ochin baseboard connected to Arducam's OV2311 with global shutter and a resolution of 1600 by 1300. The position data this program captures is intended to be communicated over Mavlink to a Pixhawk running Ardupilot to help it pick up a payload.
https://docs.opencv.org/4.x/d5/dae/tutorial_aruco_detection.html

![image](/images/cam.jpg)

## Setup
```commandline
git clone https://github.com/YannHS/aero-aruco.git
cd aero-aruco
python -m venv --system-site-package venv
source venv/bin/activate
pip install --ignore-installed  -r requirements.txt
```

## Usage
The overall workflow is:
1. Create a `camera.json` for *your* following the template:
```json
{
  "calibration": [],
  "camera_height": 1300,
  "camera_name": "Arducam OV2311",
  "camera_width": 1600,
  "format": "Y10P" 
}
```
2. Capture an image of a chessboard or Charuco board for calibration.
3. Calculate the camera coefficients using `calibration.py` to add the calibration coefficients
to the camera file
4. Run `main.py` to use the calibration data to get marker positions using the camera


## Todo
- [x] implement image capture and saving
- [x] Calculate calibration data
- [x] Write the calibration data for future use
- [X] write a main program to determine marker locations
- [X] Implement communication over Mavlink to convey the goal to the Pixhawk flight controller
- [ ] Take into account multiple detected tags
- [ ] Take into account tag and camera offsets
- [ ] Use Automation to automate the setup of this software on a fresh Raspbian install
- [ ] Create software to visualize the location data obtained by this program