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

def moveCorners(topLeft, topRight, bottomRight, bottomLeft):
    # Set the top left corner to be (0,0) and move other points to be relative to this
    offsetX = topLeft[0]
    offsetY = topLeft[1]

    # Shift all the points down by the offset
    topLeft = (0,0)
    topRight = (topRight[0] - offsetX, topRight[1] - offsetY)
    bottomRight = (bottomRight[0] - offsetX, bottomRight[1] - offsetY)
    bottomLeft = (bottomLeft[0] - offsetX, bottomLeft[1] - offsetY)

    return (topLeft, topRight, bottomRight, bottomLeft) 

# Return the distance estimate from the camera to the tag.
def calculateDistance(topLeft, topRight, bottomRight, bottomLeft):
    sides = []
    sides.append(math.sqrt((topLeft[0] - topRight[0]) ** 2 + (topLeft[1] - topRight[1]) ** 2)) # top
    sides.append(math.sqrt((topRight[0] - bottomRight[0]) ** 2 + (topRight[1] - bottomRight[1]) ** 2)) # right
    sides.append(math.sqrt((bottomRight[0] - bottomLeft[0]) ** 2 + (bottomRight[1] - bottomLeft[1]) ** 2)) # bottom
    sides.append(math.sqrt((bottomLeft[0] - topLeft[0]) ** 2 + (bottomLeft[1] - topLeft[1]) ** 2)) # left

    averageLength = int((sides[0] + sides[1] + sides[2] + sides[3]) / 4)

    if (averageLength <= 34): # more than 30cm
        return (averageLength, (-0.83 * averageLength) + 58.3)
    elif (averageLength <= 54): # more than 20cm and less than or equal to 30cm
        return (averageLength, (-0.5 * averageLength) + 47)
    elif (averageLength <= 102): # more than 10cm and less than or equal to 20cm
        return (averageLength, (-0.2083 * averageLength) + 31.25)
    else: # less than or equal to 5cm
        return (averageLength, (-0.0862 * averageLength) + 18.8)

lastBeep = -1
# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-t", "--type", type=str,
    default="DICT_5X5_100",
    help="type of ArUCo tag to detect")
ap.add_argument("-id", "--id", type=str,
    default="1",
    help="ID of ArUCo tag to detect")
args = vars(ap.parse_args())

# Start video stream and allow pause to ensure it is ready to display
print("*** Starting Video Stream ***")
vs = VideoStream(src=1).start()
time.sleep(1.0)

arucoDict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_5X5_100)
arucoParams = cv2.aruco.DetectorParameters_create()

# loop over the frames from the video stream
while True:
    # grab the frame from the threaded video stream and resize it
    # to have a maximum width of 1000 pixels
    frame = vs.read()
    frame = imutils.resize(frame, width=1000)
    # detect ArUco markers in the input frame
    (positions, ids, _) = cv2.aruco.detectMarkers(frame,
        arucoDict, parameters=arucoParams)

    # verify *at least* one ArUco marker was detected
    if len(positions) > 0:
        ids = ids.flatten()

        # loop over the detected ArUCo corners
        for (markerCorner, markerID) in zip(positions, ids):
            isCorrectTag = args["id"] == str(markerID)

            # extract the positions of each of the corners
            topLeft = (int(markerCorner[0][0][0]),int(markerCorner[0][0][1]))
            topRight = (int(markerCorner[0][1][0]),int(markerCorner[0][1][1]))
            bottomRight = (int(markerCorner[0][2][0]),int(markerCorner[0][2][1]))
            bottomLeft = (int(markerCorner[0][3][0]),int(markerCorner[0][3][1]))

            # draw the bounding box of the ArUCo detection
            cv2.line(frame, topLeft, topRight, (0, 255, 0) if isCorrectTag else (0, 0, 255), 2)
            cv2.line(frame, topRight, bottomRight, (0, 255, 0) if isCorrectTag else (0, 0, 255), 2)
            cv2.line(frame, bottomRight, bottomLeft, (0, 255, 0) if isCorrectTag else (0, 0, 255), 2)
            cv2.line(frame, bottomLeft, topLeft, (0, 255, 0) if isCorrectTag else (0, 0, 255), 2)

            # draw the ArUco marker ID on the frame
            cv2.putText(frame, str(markerID),
                (topLeft[0], topLeft[1] - 15),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5, (0, 255, 0) if isCorrectTag else (0, 0, 255), 2)
            
            if (isCorrectTag):
                (topLeft, topRight, bottomRight, bottomLeft) = moveCorners(topLeft, topRight, bottomRight, bottomLeft)
                (averageLength, distance) = calculateDistance(topLeft, topRight, bottomRight, bottomLeft)

                cv2.putText(frame, "Tag "+str(markerID)+" found - "+"{:.1f}".format(distance)+"cm away",
                    (10,20),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5, (255, 0, 0), 2)
                if (distance <= 10 and (time.perf_counter() - lastBeep > 5 or lastBeep == -1)):
                    lastBeep = time.perf_counter()
                    NSBeep()
                    closeHand()
                    
    # show the output frame
    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF
    # if the `q` key was pressed, break from the loop
    if key == ord("q"):
        break
        
    
# do a bit of cleanup
cv2.destroyAllWindows()
vs.stop()