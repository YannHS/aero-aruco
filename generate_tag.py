'''
Aruco tag generation
Generates aruco tag image files

usage:
    generate_tag.py [-w <image width>] [-h <image height>] [-i <tag id>] [-t <aruco dictionary type>] [-o <output image file>]

usage example:
    generate_tag.py -w 100 -h 100 -i 1 -t DICT_4X4_50 -o tag.png

default values:
    -w: 100
    -h: 100
    -i: 1
    -t DICT_4X4_50
    -o tag.png
'''

import sys
import getopt
import cv2 as cv
import numpy

aruco_dicts = {
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
