'''
Aruco tag generation
Generates square aruco tag image files with specified width

usage:
    generate_tag.py [-w <image width>] [-i <tag id>] [-t <aruco dictionary type>] [-o <output image file>]

usage example:
    generate_tag.py -w 100 -i 1 -t DICT_4X4_50 -o tag.png

default values:
    -w: 100
    -i: 1
    -t DICT_4X4_50
    -o tag.png
'''

import sys
import getopt
import cv2 as cv
import numpy as np

aruco_dict = {
    'DICT_4X4_50': cv.aruco.DICT_4X4_50,
    'DICT_4X4_100': cv.aruco.DICT_4X4_100,
    'DICT_4X4_250': cv.aruco.DICT_4X4_250,
    'DICT_4X4_1000': cv.aruco.DICT_4X4_1000,
    'DICT_5X5_50': cv.aruco.DICT_5X5_50,
    'DICT_5X5_100': cv.aruco.DICT_5X5_100,
    'DICT_5X5_250': cv.aruco.DICT_5X5_250,
    'DICT_5X5_1000': cv.aruco.DICT_5X5_1000,
    'DICT_6X6_50': cv.aruco.DICT_6X6_50,
    'DICT_6X6_100': cv.aruco.DICT_6X6_100,
    'DICT_6X6_250': cv.aruco.DICT_6X6_250,
    'DICT_6X6_1000': cv.aruco.DICT_6X6_1000,
    'DICT_7X7_50': cv.aruco.DICT_7X7_50,
    'DICT_7X7_100': cv.aruco.DICT_7X7_100,
    'DICT_7X7_250': cv.aruco.DICT_7X7_250,
    'DICT_7X7_1000': cv.aruco.DICT_7X7_1000,
    'DICT_ARUCO_ORIGINAL': cv.aruco.DICT_ARUCO_ORIGINAL,
    'DICT_APRILTAG_16h5': cv.aruco.DICT_APRILTAG_16h5,
    'DICT_APRILTAG_25h9': cv.aruco.DICT_APRILTAG_25h9,
    'DICT_APRILTAG_36h10': cv.aruco.DICT_APRILTAG_36h10,
    'DICT_APRILTAG_36h11': cv.aruco.DICT_APRILTAG_36h11
}



def main():


    # Process the arguments
    args, img_names = getopt.getopt(sys.argv[1:], 'w:i:t:o:', [])

    args = dict(args)

    args.setdefault('-w', '100')
    args.setdefault('-i', '0')
    args.setdefault('-t', 'DICT_4X4_50')
    args.setdefault('-o', 'tag.png')

    width = int(args.get('-w'))
    tag_id = int(args.get('-i'))
    tag_type = str(args.get('-t'))
    tag_image_file = str(args.get('-o'))

    # Create the tag image with all zeros
    tag = np.zeros((width, width, 1), dtype="uint8")

    # get the actual tag from the specified argument
    aruco_tag = cv.aruco.getPredefinedDictionary(aruco_dict[tag_type])

    # draw the actual marker bitmap
    cv.aruco.generateImageMarker(aruco_tag, tag_id, width, tag, 1)

    # write the generated ArUCo tag to disk
    cv.imwrite(tag_image_file, tag)

main()