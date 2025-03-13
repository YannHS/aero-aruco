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
from pymavlink import mavutil
from time import sleep, time


# The Craft class connects to the flight controller and sends controlling messages
class Craft:
    def __init__(self, connectstr):
        self.debug = False
        self.mode = None
        self.connected = None
        self.vehicle = None
        self.connect(connectstr)
    def connect(self, connectstr):
        try:
            # self.vehicle = connect(connectstr, wait_ready=True, rate=1)
            # self.vehicle = connect(connectstr, wait_ready=True)
            # self.vehicle = connect(connectstr, wait_ready=['system_status','mode'], baud=921600)
            self.vehicle = mavutil.mavlink_connection(connectstr, wait_ready=['system_status','mode'], baud=57600)
            self.connected = True
        except:
            print("Error connecting to vehicle")
            self.connected = False
    # Define function to send distance_message mavlink message for mavlink based rangefinder, must be >10hz
    # http://mavlink.org/messages/common#DISTANCE_SENSOR
    def send_distance_message(self, dist):
        msg = self.vehicle.message_factory.distance_sensor_encode(
            0,          # time since system boot, not used
            1,          # min distance cm
            10000,      # max distance cm
            dist,       # current distance, must be int
            0,          # type = laser?
            0,          # onboard id, not used
            mavutil.mavlink.MAV_SENSOR_ROTATION_PITCH_270, # must be set to MAV_SENSOR_ROTATION_PITCH_270 for mavlink rangefinder, represents downward facing
            0           # covariance, not used
        )
        self.vehicle.send_mavlink(msg)
        self.vehicle.flush()
        #if args.verbose:
            #log.debug("Sending mavlink distance_message:" +str(dist))
    # Define function to send landing_target mavlink message for mavlink based precision landing
    # http://mavlink.org/messages/common#LANDING_TARGET
    def send_land_message(self, x,y,z, time_usec=0, target_num=0):
        msg = self.vehicle.message_factory.landing_target_encode(
            time_usec,          # time target data was processed, as close to sensor capture as possible
            target_num,          # target num, not used
            mavutil.mavlink.MAV_FRAME_BODY_NED, # frame, not used
            x,          # X-axis angular offset, in radians
            y,          # Y-axis angular offset, in radians
            z,          # distance, in meters
            0,          # Target x-axis size, in radians
            0,          # Target y-axis size, in radians
            0,          # x	float	X Position of the landing target on MAV_FRAME
            0,          # y	float	Y Position of the landing target on MAV_FRAME
            0,          # z	float	Z Position of the landing target on MAV_FRAME
            (1,0,0,0),  # q	float[4]	Quaternion of landing target orientation (w, x, y, z order, zero-rotation is 1, 0, 0, 0)
            2,          # type of landing target: 2 = Fiducial marker
            1,          # position_valid boolean
        )
        self.vehicle.send_mavlink(msg)
        self.vehicle.flush()
        #if args.verbose:
            #log.debug("Sending mavlink landing_target - time_usec:{:.0f}, x:{}, y:{}, z:{}".format(time_usec, str(x), str(y), str(z)))




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


    # Do flight controller setup
    craft = Craft("/dev/ttyS0")


    if 'PLND_BUFFER' in craft.vehicle.parameters:
        craft.vehicle.parameters['PLND_BUFFER'] = 250



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

        # Make sure a tag was actually detected
        if len(aruco_corners) > 0:

            for x in aruco_corners:
                flag, rvec, tvec = cv.solvePnP(obj_points, x, cam_matrix, dist_coefficients)
                print("Rotation:", '\n', rvec, '\n', "Translation:", '\n', tvec)

        craft.send_land_message(0, 0, 69)


main()