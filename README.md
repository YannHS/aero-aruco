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
python image_capture.py -c 1 -w 1920 -h 1080
python calibration.py -w 9 -h 6 --square_size 22 cam_output/0_capture.png
python main.py -c calibration.json -w 1920 -h 1080
```

## Todo
- [x] implement image capture and saving
- [x] Calculate calibration data
- [x] Write the calibration data for future use
- [ ] write a main program to determine marker locations