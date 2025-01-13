## Dependencies
`opencv-python`
`numpy`
`getopt`
`pickle`

## Usage
The intended workflow is:
1. Capture an image of a chessboard using `image_capture.py` 
2. Calculate the camera coefficients using `calibration.py` to be saved for later
3. Run `main.py` to use the calibration data to get marker positions using the camera

Example:
```commandline
python image_capture.py -c 1 -w 1920 -h 1080 # This captures an image for calibration
python calibration.py -w 9 -h 6 --square_size 22 cam_output/0_capture.png # This determines distortion coefficiants from the image
python generate_tag.py # Generates the Aruco tag for detecting
python main.py -c calibration.json -w 1920 -h 1080 # This runs the main tag detection and pose estimation program
```

## Todo
- [x] implement image capture and saving
- [x] Calculate calibration data
- [x] Write the calibration data for future use
- [X] write a main program to determine marker locations
- [ ] Implement communication over Mavlink to convey the goal to the Pixhawk flight controller