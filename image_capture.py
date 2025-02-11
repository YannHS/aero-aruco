'''
camera image capture
reads multiple camera images and writes them to a directory

usage:
    image_capture.py [-o <output path>] [-c <image count>] [-j <camera json>]

usage example:
    image_capture.py -c 5

default values:
    -o: ./cam_output/
    -c 1
    -j camera.json
'''


import sys
import getopt
import os
import cv2 as cv
import json

def main():
    # Get CMD arguments
    try:
        args, img_names = getopt.getopt(sys.argv[1:], 'o:c:j:i', [])
    except:
        # print help information and exit
        print("""usage:
    image_capture.py [-o <output path>] [-c <image count>] [-j <camera json>]

usage example:
    image_capture.py -c 5""")
    args = dict(args)

    # Set the default values
    args.setdefault('-o', './cam_output/')
    args.setdefault('-c', 1)
    args.setdefault('-j', "camera.json")

    # Store the image output Directory
    image_output_dir = str(args.get('-o'))
    imgcount = int(args.get('-c'))
    camera_json = str(args.get('-j'))

    # Read the camera parameters
    camera_params = json.loads(open(camera_json, 'r').read())


    # Create the output folder if it does not already exist
    if not os.path.isdir(image_output_dir):
        os.mkdir(image_output_dir)

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
        camera.configure(camera.create_preview_configuration(main={"size": (camera_params["camera_width"], camera_params["camera_height"])}))
        camera.start()
    else:
        print("Invalid Camera capture method")
        return

    for num in range(imgcount):
        input("Enter to capture")
        if camera_params["capture_method"] == "OpenCV":
            #Capture openCV frame
            ret, frame = cam.read()
        elif camera_params["capture_method"] == "PiCamera":
            # Create pi camera
            # Capture picamera frame

            frame = camera.capture_array()
        else:
            print("Invalid Camera capture method")
            return -1




        # Check if image acquisition is successful
        if True:
            filename = os.path.join(image_output_dir, str(num) + '_capture.png')
            cv.imwrite(filename, frame)
        else:
            print("failed to grab frame")
            return -1


main()