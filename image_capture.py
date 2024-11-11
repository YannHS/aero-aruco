'''
camera image capture
reads multiple camera images using OpenCV and writes them to a directory

usage:
    image_capture.py [-o <output path>] [-c <image count>] [-w <width>] [-h <height>]

usage example:
    image_capture.py -w 640 -h 480 -o ./output -c 5

default values:
    -w: 640
    -h: 480
    -o: ./cam_output/
    -c 1
'''


import sys
import getopt
import os
import cv2 as cv
import time

def main():
    # Get CMD arguments
    try:
        args, img_names = getopt.getopt(sys.argv[1:], 'o:c:w:h:e:d:', [])
    except:
        # print help information and exit
        print("""usage:
    image_capture.py [-o <output path>] [-c <image count>] [-w <width>] [-h <height>] [-e <exposure>]

usage example:
    image_capture.py -w 640 -h 480 -o ./output -c 5 -e 0""")
    args = dict(args)

    # Set the default values
    args.setdefault('-o', './cam_output/')
    args.setdefault('-c', 1)
    args.setdefault('-w', 640)
    args.setdefault('-h', 480)
    args.setdefault('-e', 0)

    # Store the image output Directory
    image_output_dir = str(args.get('-o'))
    imgcount = int(args.get('-c'))


    # Create the output folder if it does not already exist
    if not os.path.isdir(image_output_dir):
        os.mkdir(image_output_dir)

    cam = cv.VideoCapture(0)

    for num in range(imgcount):
        input("Enter to capture")
        # Read the image from the camera

        cam.set(cv.CAP_PROP_FRAME_WIDTH, int(args.get('-w')))
        cam.set(cv.CAP_PROP_FRAME_HEIGHT, int(args.get('-h')))
        cam.set(cv.CAP_PROP_EXPOSURE, int(args.get('-e')))
        cam.set(cv.CAP_PROP_FPS, 60)
        ret, frame = cam.read()

        # Check if image acquisition is successful
        if ret:
            filename = os.path.join(image_output_dir, str(num) + '_capture.png')
            cv.imwrite(filename, frame)
        else:
            print("failed to grab frame")
            return -1


main()