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
import cv2 as cv
import numpy as np
import json




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

    # set the camera
    cam = cv.VideoCapture(0)

    # set camera params
    cam.set(cv.CAP_PROP_FRAME_WIDTH, int(args.get('-w')))
    cam.set(cv.CAP_PROP_FRAME_HEIGHT, int(args.get('-h')))
    cam.set(cv.CAP_PROP_EXPOSURE, int(args.get('-e')))
    cam.set(cv.CAP_PROP_FPS, 60)

    # Read the calibration file
    calibration_file = open(calibration_data_file, 'r')
    json_camera_data = json.loads(calibration_file.read())
    cam_matrix = json_camera_data[0]
    dist_coefficients = json_camera_data[1]

    aruco_dict = cv.aruco.getPredefinedDictionary(cv.aruco.DICT_4X4_50)
    aruco_parameters = cv.aruco.DetectorParameters()
    aruco_detector = cv.aruco.ArucoDetector(aruco_dict, aruco_parameters)


    while True:
        # aquire camera image
        ret, frame = cam.read()
        frame = cv.cvtColor(frame, cv.COLOR_RGBA2BGR)
        # Check if image acquisition is successful
        if ret:
            # Detect the tag corners
            corners, ids, rejected = aruco_detector.detectMarkers(frame)

            # Make sure a tag was actually detected
            if ids != None:

                for x in corners:
                    flag, rvec, tvec = cv.solvePnP(cam_matrix, dist_coefficients)
        else:
            print("failed to grab frame")
            return -1


main()