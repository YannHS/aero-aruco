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
import cv2 as cv
import numpy

def main():
    # Get CMD arguments
    try:
        args, img_names = getopt.getopt(sys.argv[1:], 'c:w:h:', [])
    except:
        # print help information and exit
        print("""usage:
    main.py [-c <calibration file>] [-w <capture width>] [-h <capture height>]
""")
    args = dict(args)

    # Set the default values
    args.setdefault('-c', 'calibration.json')
    args.setdefault('-w', 1920)
    args.setdefault('-h', 1080)

    # Store the image output Directory
    image_output_dir = str(args.get('-o'))
    imgcount = int(args.get('-c'))

    # set the camera
    cam = cv.VideoCapture(0)

    # set camera params
    cam.set(cv.CAP_PROP_FRAME_WIDTH, int(args.get('-w')))
    cam.set(cv.CAP_PROP_FRAME_HEIGHT, int(args.get('-h')))
    cam.set(cv.CAP_PROP_EXPOSURE, int(args.get('-e')))
    cam.set(cv.CAP_PROP_FPS, 60)


    while True:
        # aquire camera image
        ret, frame = cam.read()
        # Check if image acquisition is successful
        if ret:
            pass
        else:
            print("failed to grab frame")
            return -1


main()