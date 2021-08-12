import numpy as np
import argparse
import cv2
import sys

# Parse 'id' Argument Provided
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--id", type=int, required=True,
	help="ID of ArUCo tag")
args = vars(ap.parse_args())

tag_id = args["id"]

# load the ArUCo dictionary
arucoDict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_5X5_100)

# generate the ArUCo tag on the output image as a 300x300 image
print("[INFO] generating ArUCo tag type 'aruco_5x5_100' with ID '{}'".format(tag_id))
tag = np.zeros((300, 300, 1), dtype="uint8")
cv2.aruco.drawMarker(arucoDict, tag_id, 300, tag, 1)

# write the generated ArUCo tag with unique name for each id
cv2.imwrite('id_'+str(tag_id)+'.png', tag)

