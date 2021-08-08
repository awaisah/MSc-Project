# import the necessary packages
from imutils.video import VideoStream
import argparse
import imutils
import time
import cv2
import sys
import math
import time
from AppKit import NSBeep
import threading

from bluetooth import *

global nextCommand
nextCommand = ""

loop = asyncio.get_event_loop()
bluetoothThread = threading.Thread(target=start, args=(loop, ))
bluetoothThread.start()

def say(msg = "Finish", voice = "Victoria"):
    os.system(f'say -v {voice} {msg}')

def rotateCorners(corners):
	(topLeft, topRight, bottomRight, bottomLeft) = corners

	# Set the top left corner to be (0,0) and move other points to be relative to this
	offsetX = 0 # topLeft[0]
	offsetY = 0 # topLeft[1]

	# topLeft[0] = 0
	# topLeft[1] = 0

	topRight[0] = topRight[0] - offsetX
	topRight[1] = topRight[1] - offsetY

	bottomRight[0] = bottomRight[0] - offsetX
	bottomRight[1] = bottomRight[1] - offsetY

	bottomLeft[0] = bottomLeft[0] - offsetX
	bottomLeft[1] = bottomLeft[1] - offsetY

	diagonals = []
	diagonals.append(math.sqrt((bottomLeft[0] - topRight[0]) ** 2 + (bottomLeft[1] - topRight[1]) ** 2))
	diagonals.append(math.sqrt((topLeft[0] - bottomRight[0]) ** 2 + (topLeft[1] - bottomRight[1]) ** 2))

	sides = []
	sides.append(math.sqrt((topLeft[0] - topRight[0]) ** 2 + (topLeft[1] - topRight[1]) ** 2)) # top
	sides.append(math.sqrt((topRight[0] - bottomRight[0]) ** 2 + (topRight[1] - bottomRight[1]) ** 2)) # right
	sides.append(math.sqrt((bottomRight[0] - bottomLeft[0]) ** 2 + (bottomRight[1] - bottomLeft[1]) ** 2)) # bottom
	sides.append(math.sqrt((bottomLeft[0] - topLeft[0]) ** 2 + (bottomLeft[1] - topLeft[1]) ** 2)) # left

	return (topLeft, topRight, bottomRight, bottomLeft, sides) 

def toDistance(width):
    if (width <= 54):
        return int(-0.5 * width + 47)
    elif (width <= 77):
        return int(-0.21739130434783 * width + 31.739130434783)
    else:
        return int(-0.19607843137255 * width + 30.588235294118)

    # return int(0.044 * width * width - 0.615 * width + 48.14)

lastBeep = -1
# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-t", "--type", type=str,
    default="DICT_5X5_100",
    help="type of ArUCo tag to detect")
args = vars(ap.parse_args())


# define names of each possible ArUco tag OpenCV supports
ARUCO_DICT = {
    "DICT_4X4_50": cv2.aruco.DICT_4X4_50,
    "DICT_4X4_100": cv2.aruco.DICT_4X4_100,
    "DICT_4X4_250": cv2.aruco.DICT_4X4_250,
    "DICT_4X4_1000": cv2.aruco.DICT_4X4_1000,
    "DICT_5X5_50": cv2.aruco.DICT_5X5_50,
    "DICT_5X5_100": cv2.aruco.DICT_5X5_100,
    "DICT_5X5_250": cv2.aruco.DICT_5X5_250,
    "DICT_5X5_1000": cv2.aruco.DICT_5X5_1000,
    "DICT_6X6_50": cv2.aruco.DICT_6X6_50,
    "DICT_6X6_100": cv2.aruco.DICT_6X6_100,
    "DICT_6X6_250": cv2.aruco.DICT_6X6_250,
    "DICT_6X6_1000": cv2.aruco.DICT_6X6_1000,
    "DICT_7X7_50": cv2.aruco.DICT_7X7_50,
    "DICT_7X7_100": cv2.aruco.DICT_7X7_100,
    "DICT_7X7_250": cv2.aruco.DICT_7X7_250,
    "DICT_7X7_1000": cv2.aruco.DICT_7X7_1000,
    "DICT_ARUCO_ORIGINAL": cv2.aruco.DICT_ARUCO_ORIGINAL,
    "DICT_APRILTAG_16h5": cv2.aruco.DICT_APRILTAG_16h5,
    "DICT_APRILTAG_25h9": cv2.aruco.DICT_APRILTAG_25h9,
    "DICT_APRILTAG_36h10": cv2.aruco.DICT_APRILTAG_36h10,
    "DICT_APRILTAG_36h11": cv2.aruco.DICT_APRILTAG_36h11
}

# verify that the supplied ArUCo tag exists and is supported by
# OpenCV
if ARUCO_DICT.get(args["type"], None) is None:
    print("[INFO] ArUCo tag of '{}' is not supported".format(
        args["type"]))
    sys.exit(0)
# load the ArUCo dictionary and grab the ArUCo parameters
print("[INFO] detecting '{}' tags...".format(args["type"]))
arucoDict = cv2.aruco.Dictionary_get(ARUCO_DICT[args["type"]])
arucoParams = cv2.aruco.DetectorParameters_create()
# initialize the video stream and allow the camera sensor to warm up
print("[INFO] starting video stream...")
vs = VideoStream(src=1).start()
time.sleep(2.0)

# loop over the frames from the video stream
while True:
    # grab the frame from the threaded video stream and resize it
    # to have a maximum width of 1000 pixels
    frame = vs.read()
    frame = imutils.resize(frame, width=1000)
    # detect ArUco markers in the input frame
    (corners, ids, rejected) = cv2.aruco.detectMarkers(frame,
        arucoDict, parameters=arucoParams)

    # verify *at least* one ArUco marker was detected
    if len(corners) > 0:
        # flatten the ArUco IDs list
        ids = ids.flatten()

        averageLength = 100

        # loop over the detected ArUCo corners
        for (markerCorner, markerID) in zip(corners, ids):
            # extract the marker corners (which are always returned
            # in top-left, top-right, bottom-right, and bottom-left
            # order)
            corners = markerCorner.reshape((4, 2))
            # (topLeft, topRight, bottomRight, bottomLeft) = corners
            (topLeft, topRight, bottomRight, bottomLeft, sides) = rotateCorners(corners)
            # convert each of the (x, y)-coordinate pairs to integers
            topRight = (int(topRight[0]), int(topRight[1]))
            bottomRight = (int(bottomRight[0]), int(bottomRight[1]))
            bottomLeft = (int(bottomLeft[0]), int(bottomLeft[1]))
            topLeft = (int(topLeft[0]), int(topLeft[1]))

            averageLength = int((sides[0] + sides[1] + sides[2] + sides[3]) / 4)

            # draw the bounding box of the ArUCo detection
            cv2.line(frame, topLeft, topRight, (0, 255, 0), 2)
            cv2.line(frame, topRight, bottomRight, (0, 255, 0), 2)
            cv2.line(frame, bottomRight, bottomLeft, (0, 255, 0), 2)
            cv2.line(frame, bottomLeft, topLeft, (0, 255, 0), 2)

            cv2.line(frame, [0,0], [averageLength, 0], (0, 255, 0), 2)
            cv2.line(frame, [averageLength, 0], [averageLength, averageLength], (0, 255, 0), 2)
            cv2.line(frame, [averageLength, averageLength], [0, averageLength], (0, 255, 0), 2)
            cv2.line(frame, [0, averageLength], [0,0], (0, 255, 0), 2)
            # compute and draw the center (x, y)-coordinates of the
            # ArUco marker
            cX = int((topLeft[0] + bottomRight[0]) / 2.0)
            cY = int((topLeft[1] + bottomRight[1]) / 2.0)
            cv2.circle(frame, (cX, cY), 4, (0, 0, 255), -1)
            # draw the ArUco marker ID on the frame
            cv2.putText(frame, str(markerID),
                (topLeft[0], topLeft[1] - 15),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5, (0, 255, 0), 2)
            cv2.putText(frame, str(averageLength) + " - " + str(toDistance(averageLength)) + "cm",
                [10,20],
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5, (0, 0, 255), 2)
    # show the output frame
    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF
    # if the `q` key was pressed, break from the loop
    if key == ord("q"):
        break
    if (len(corners) > 0 and averageLength >= 100):
        # sys.stdout.write('\a')
        # sys.stdout.flush()
        print(lastBeep)
        if (time.perf_counter() - lastBeep > 5 or lastBeep == -1):
            lastBeep = time.perf_counter()
            NSBeep()
            closeHand()
    
# do a bit of cleanup
cv2.destroyAllWindows()
vs.stop()