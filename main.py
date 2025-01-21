'''
Aruco pose estimation
uses live camera data to get Aruco tag pose

usage:
    main.py [-c <calibration file>] [-w <capture width>] [-h <capture height>]

usage example:
    main.py -c calibration.json -w 1920 -h 1080

default values:
    -c: calibration.json
'''

import os
import sys
import getopt
import time

import cv2 as cv
import numpy as np
import json
from picamera2 import Picamera2




def main():
    # Get CMD arguments
    try:
        args, img_names = getopt.getopt(sys.argv[1:], 'c:w:h:e', [])
    except:
        # print help information and exit
        print("""usage:
    main.py [-c <calibration file>] [-w <capture width>] [-h <capture height>] [-e <exposure>]
""")
    args = dict(args)

    # Set the default values
    args.setdefault('-c', 'calibration.json')
    args.setdefault('-w', 1920)
    args.setdefault('-h', 1080)
    args.setdefault('-e', 0)

    # Assign arguments to variables
    calibration_data_file = str(args.get('-c'))

    # set the camera OpenCV cameras
    # cam = cv.VideoCapture(0, cv.CAP_FFMPEG)

    # set camera params vor OpenVC camera
    # cam.set(cv.CAP_PROP_FRAME_WIDTH, int(args.get('-w')))
    # cam.set(cv.CAP_PROP_FRAME_HEIGHT, int(args.get('-h')))
    # cam.set(cv.CAP_PROP_EXPOSURE, int(args.get('-e')))
    # cam.set(cv.CAP_PROP_FPS, 60)

    # set the camera for the Pi
    camera = Picamera2()
    camera.configure(camera.create_preview_configuration(main={"size": (1600, 1300)}))
    camera.start()



    # Read the calibration file
    calibration_file = open(calibration_data_file, 'r')
    json_camera_data = json.loads(calibration_file.read())
    cam_matrix = np.array(json_camera_data[0])
    dist_coefficients = np.array(json_camera_data[1])

    aruco_dict = cv.aruco.getPredefinedDictionary(cv.aruco.DICT_4X4_50)
    aruco_parameters = cv.aruco.DetectorParameters()
    aruco_detector = cv.aruco.ArucoDetector(aruco_dict, aruco_parameters)

    # Set coordinate system
    markerLength = 93/2
    obj_points = np.array([
        [-markerLength, markerLength, 0],
        [markerLength, markerLength, 0],
        [markerLength, -markerLength, 0],
        [-markerLength, -markerLength, 0]
    ], dtype=np.float32)

    while True:
        # aquire camera image
        ret, frame = cam.read()
        frame = cv.cvtColor(frame, cv.COLOR_RGBA2BGR)
        # Check if image acquisition is successful
        if True:
            # Detect the tag corners
            aruco_corners, aruco_ids, rejected = aruco_detector.detectMarkers(frame)

            # Make sure a tag was actually detected
            if len(aruco_corners) > 0:

                for x in aruco_corners:
                    flag, rvec, tvec = cv.solvePnP(obj_points, x, cam_matrix, dist_coefficients)
                    print("Rotation:", '\n', rvec, '\n', "Translation:", '\n', tvec)


main()