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

from pcbnew import VECTOR3D
from pymavlink import mavutil
import pymavlink
from time import sleep, time
import math

from pymavlink.rotmat import Vector3


def wait_heartbeat(m):
    '''wait for a heartbeat so we know the target system IDs'''
    print("Waiting for APM heartbeat")
    msg = m.recv_match(type='HEARTBEAT', blocking=True)
    print("Heartbeat from APM (system %u component %u)" % (m.target_system, m.target_component))


def compute_position(detected_corners, aruco_ids, pad_tags, payload_tag_ID, camera_offset, cam_matrix, dist_coefficients):
    """
    Given the input detected tags, pad tags, payload tag, and camera offset vectors, this function returns a
    single position vector for sending to the flight controller
    """

    # Don't try to compute anything if no tags were detected
    if len(detected_corners) == 0:
        return False

    # Create a dict to store the detected tags along with their positions
    detected_tags = {}



    # Go through the detected tags
    for x in range(len(detected_corners)):
        # Get the measured length of the tag being detected
        markerLength = pad_tags[str(aruco_ids[x])] / 2

        # Set coordinate system
        obj_points = np.array([
            [-markerLength, markerLength, 0],
            [markerLength, markerLength, 0],
            [markerLength, -markerLength, 0],
            [-markerLength, -markerLength, 0]
        ], dtype=np.float32)

        # Compute the rotation and rotation
        flag, rvec, tvec = cv.solvePnP(obj_points, detected_corners[x], cam_matrix, dist_coefficients)

        # Add the tag ID and position to the detected_tags dict
        detected_tags[int(aruco_ids[x][0])] = tvec

        # Todo: Implement a system that calculates the final position using the averaged individual position of each tag

        if detected_tags.get(payload_tag_ID) is not None:
            return detected_tags[payload_tag_ID]
        else:
            return False


def main():
    # Get CMD arguments
    try:
        args, img_names = getopt.getopt(sys.argv[1:], 'c:p:m', [])
    except:
        # print help information and exit
        print("""usage:
    main.py [-c <camera file>] [-p <pad file>] [-m <mavlink communication True/False>]
""")
    args = dict(args)

    # Set the default values
    args.setdefault('-c', 'camera.json')
    args.setdefault('-p', 'pad.json')
    args.setdefault('-m', 'True')


    # Assign arguments to variables
    calibration_data_file = str(args.get('-c'))
    pad_data_file = str(args.get('-p'))
    use_mavlink = bool(args.get('-m'))
    #marker_size = int(args.get('-s'))

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



    # Read the landing lad parameters
    pad_params = json.loads(open(pad_data_file, 'r').read())

    if use_mavlink:
        # Start a connection listening on the serial port
        the_connection = mavutil.mavlink_connection("/dev/ttyS0", 57600)

        # Wait for the first heartbeat
        wait_heartbeat(the_connection)

    # Main Program loop
    while True:
        sleep(0.1)

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

        # compute the location of the payload
        computed_position = compute_position(aruco_corners,
                                             aruco_ids,
                                             pad_params["pad_tags"],
                                             int(pad_params["payload_tag_ID"]),
                                             camera_params["camera_offset"],
                                             cam_matrix,
                                             dist_coefficients)

        # Make sure that tags were actually detected
        if computed_position != False and use_mavlink:
            # Send the location to the flight controller
            the_connection.mav.landing_target_send(int(time() * 1000000),  # Time since "boot"
                                                 0,  # not used
                                                 mavutil.mavlink.MAV_FRAME_BODY_NED,  # Reference frame
                                                 0,  # angle_x, not used since we have position
                                                 0,  # angle_y, not used since we have position
                                                 0,
                                                 0,  # not used
                                                 0,  # not used
                                                 computed_position[0],  # x (Forward)
                                                 computed_position[1],  # y (Right)
                                                 computed_position[2],  # z (Down)
                                                 [0, 0, 0, 1],  # not used
                                                 0,  # not used
                                                 1  # marks that we want to use x, y, z coords
                                                 )

# ======================================================================================================================


main()

