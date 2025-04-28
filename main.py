'''
Aruco pose estimation
uses live camera data to get Aruco tag pose

usage:
    main.py [-c <camera file>] [-p <pad file>] [-m <send mavlink data>]

usage example:
    main.py -c camera.json -p pad.json -m

default values:
    -c: dingus
'''

import sys
import getopt
import time
import cv2 as cv
import numpy as np
import json
from pymavlink import mavutil
from time import sleep, time
import math


def rotate_vector_3d(position, rot_vector):
    """
    Rotate a 3D position vector using Euler angles.
    This function was taken from Open-ai's 3o mini LLM, this function should not be trusted

    Args:
        position (np.ndarray): A NumPy array of shape (3,) representing (x, y, z) in meters.
        rot_vector (np.ndarray): A NumPy array of shape (3,) where:
                                 rot_vector[0] is the rotation about the x-axis (in radians),
                                 rot_vector[1] is the rotation about the y-axis (in radians),
                                 rot_vector[2] is the rotation about the z-axis (in radians).

    Returns:
        np.ndarray: The rotated 3D position vector.
    """
    rx, ry, rz = rot_vector  # Extract Euler angles for rotation about each axis.

    # Rotation matrix about the x-axis.
    Rx = np.array([
        [1, 0, 0],
        [0, np.cos(rx), -np.sin(rx)],
        [0, np.sin(rx),  np.cos(rx)]
    ])

    # Rotation matrix about the y-axis.
    Ry = np.array([
        [ np.cos(ry), 0, np.sin(ry)],
        [0, 1, 0],
        [-np.sin(ry), 0, np.cos(ry)]
    ])

    # Rotation matrix about the z-axis.
    Rz = np.array([
        [np.cos(rz), -np.sin(rz), 0],
        [np.sin(rz),  np.cos(rz), 0],
        [0, 0, 1]
    ])

    # Combine the rotations. Here we apply Rx, then Ry, then Rz.
    # Note: Matrix multiplication is not commutative so the order matters.
    R = Rz @ Ry @ Rx

    # Apply rotation
    rotated_position = R @ position
    return rotated_position


def wait_heartbeat(m):
    '''wait for a heartbeat so we know the target system IDs'''
    print("Waiting for APM heartbeat")
    msg = m.recv_match(type='HEARTBEAT', blocking=True)
    print("Heartbeat from APM (system %u component %u)" % (m.target_system, m.target_component))

def average_vectors(vector_list):
    avg_vec = np.array([0, 0, 0], dtype=np.float32)
    for x in range(vector_list.length):
        avg_vec += vector_list[x] / vector_list.length
    return avg_vec


def compute_position(detected_corners, aruco_ids, pad_tags, payload_tag_ID, camera_offset, cam_matrix, dist_coefficients):
    """
    Given the input detected tags, pad tags, payload tag, and camera offset vectors, this function returns a
    single position vector for sending to the flight controller
    """

    # Initialize the return vector
    final_vec = False

    # Don't try to compute anything if no tags were detected
    if len(detected_corners) == 0:
        return False

    # Create a dict to store the detected tags along with their positions
    detected_tags = {}

    # Go through the tag corners and add the computed positions to the detected tags dict
    for x in range(len(detected_corners)):
        # Check if we care about the particular tag
        if pad_tags.get(str(aruco_ids[x][0])) is not None:

            # Get the measured length of the tag being detected
            markerLength = pad_tags[str(aruco_ids[x][0])][0] / 2

            # Set coordinate system
            obj_points = np.array([
                [-markerLength, markerLength, 0],
                [markerLength, markerLength, 0],
                [markerLength, -markerLength, 0],
                [-markerLength, -markerLength, 0]
            ], dtype=np.float32)

            # Compute the rotation and rotation
            flag, rvec, tvec = cv.solvePnP(obj_points, detected_corners[x], cam_matrix, dist_coefficients, flags=cv.SOLVEPNP_IPPE_SQUARE)

            # Add the tag ID and position to the detected_tags dict
            detected_tags[int(aruco_ids[x][0])] = (tvec.flatten(), rvec.flatten())

    # Implement a system that calculates the final position using the averaged individual position of each tag

    # check if the payload tag was detected
    if detected_tags.get(payload_tag_ID) is not None:

        # Payload has only one tag, so no offset needs to be applied.
        final_vec = rotate_vector_3d(0.001*detected_tags[payload_tag_ID][0], camera_offset[1]) + np.array(camera_offset[0], dtype=np.float32)
    else:
        # DLZ requires tags to be offset
        return False


    return final_vec


def main():

    # Get CMD arguments
    try:
        args, img_names = getopt.getopt(sys.argv[1:], 'c:p:m:v', [])
    except:
        # print help information and exit
        print("""usage:
    main.py [-c <camera file>] [-p <pad file>] [-m <mavlink communication true/false>] [-v <GUI true/false>]
""")
    args = dict(args)

    # Set the default values
    args.setdefault('-c', 'camera.json')
    args.setdefault('-p', 'pad.json')
    args.setdefault('-m', 'true')
    args.setdefault('-v', 'false')


    # Assign arguments to variables
    calibration_data_file = str(args.get('-c'))
    pad_data_file = str(args.get('-p'))
    use_mavlink = args.get('-m').lower() == 'true'
    use_GUI = args.get('-v').lower() == 'true'

    # start the visualizer if the argument was set
    if use_GUI:
        import vector_vis
        vector_vis.start_visualizer()

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
        sleep(0.03)

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
        if not (computed_position is False) and use_mavlink:
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

            # Print the computed result to the console for debugging
            print(computed_position)
# ======================================================================================================================


main()

