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

import sys
import getopt
import time

import cv2 as cv
import numpy as np
import json




def main():
    # Get CMD arguments
    try:
        args, img_names = getopt.getopt(sys.argv[1:], 'c:s', [])
    except:
        # print help information and exit
        print("""usage:
    main.py [-c <camera_file>] [-s <aruco tag size>]
""")
    args = dict(args)

    # Set the default values
    args.setdefault('-c', 'camera.json')
    args.setdefault('-s', '100')

    # Assign arguments to variables
    calibration_data_file = str(args.get('-c'))
    marker_size = int(args.get('-s'))

    # Read the camera parameters
    camera_params = json.loads(open(calibration_data_file, 'r').read())

    if camera_params["capture_method"] == "OpenCV":
        # Create OpenCV cam
        cam = cv.VideoCapture(0)

        # set OpenCV camera params
        cam.set(cv.CAP_PROP_FRAME_WIDTH, camera_params["camera_width"])
        cam.set(cv.CAP_PROP_FRAME_HEIGHT, camera_params["camera_height"])

    elif camera_params["capture_method"] == "PiCamera":
        from picamera2 import Picamera2
        # Create pi camera
        camera = Picamera2()
        camera.configure(camera.create_preview_configuration(
            main={"size": (camera_params["camera_width"], camera_params["camera_height"])}))
        camera.start()
    else:
        print("Invalid Camera capture method")
        return

    # assign the separate calibration matrices
    cam_matrix = np.array(camera_params["calibration"][0])
    dist_coefficients = np.array(camera_params["calibration"][1])

    # Set the aruco dict
    aruco_dict = cv.aruco.getPredefinedDictionary(cv.aruco.DICT_4X4_50)
    aruco_parameters = cv.aruco.DetectorParameters()
    aruco_detector = cv.aruco.ArucoDetector(aruco_dict, aruco_parameters)

    # Set coordinate system
    markerLength = marker_size/2
    obj_points = np.array([
        [-markerLength, markerLength, 0],
        [markerLength, markerLength, 0],
        [markerLength, -markerLength, 0],
        [-markerLength, -markerLength, 0]
    ], dtype=np.float32)


    # Main Program loop
    while True:
        # aquire camera image
        if camera_params["capture_method"] == "OpenCV":
            #Capture openCV frame
            ret, frame = cam.read()
        elif camera_params["capture_method"] == "PiCamera":
            # Create pi camera
            # Capture picamera frame

            frame = camera.capture_array()

        # Make it monochrome
        frame = cv.cvtColor(frame, cv.COLOR_RGBA2BGR)

        # Detect the tag corners
        aruco_corners, aruco_ids, rejected = aruco_detector.detectMarkers(frame)

        # Make sure a tag was actually detected
        if len(aruco_corners) > 0:

            for x in aruco_corners:
                flag, rvec, tvec = cv.solvePnP(obj_points, x, cam_matrix, dist_coefficients)
                print("Rotation:", '\n', rvec, '\n', "Translation:", '\n', tvec)


main()