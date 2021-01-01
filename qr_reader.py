import cv2
import threading
import copy
import time
from math import atan, pi

# Constants
WINDOW_NAME = "Camera view"

# Global variables
CURRENT_TILT = 0            # degrees
MOST_SIGNIFICANT_TILT = 0   # degrees

# Initialises user's camera and fetches QRCodeDetector class from cv2.
cam = cv2.VideoCapture(0)
qr_detector = cv2.QRCodeDetector()


#######################
#                     #
#  PRIVATE FUNCTIONS  #
#                     #
#######################


# Reads frame from user's camera. Returns that frame (RGB).
def __readFrame():
    _, frame = cam.read()
    return frame


# Find QR code coordinates from image.
# If there is NOT a QR code in image returns None
# If there IS a QR code in image returns coordinates of its corners like [(x0,y0),(x1,y1),(x2,y2),(x3,y3)]
def __getQRCodeCoordinates(img):
    try:
        is_qr_shown, raw_coords = qr_detector.detect(img)
        if is_qr_shown:
            coords = __processedCoords(raw_coords)
            #if checkCoords(coords):
            return coords
    except cv2.error:
        print("DEBUG: cv2.error")
    return []


# Given raw coordinates like [[[x1, y1]], [[x2, y2]], ..., [[xn yn]]] returns coordinates like [(x0,y0),(x1,y1),(x2,y2), ..., (xn,yn)]
def __processedCoords(raw_coordinates):
    processed = []
    for i in range(len(raw_coordinates[0])):
        coord = (int(raw_coordinates[0][i][0]), int(raw_coordinates[0][i][1]))
        processed.append(coord)
    return processed


# Draws a closed polygon on image based on coords.
def __drawROI(img, coords):
    colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
    for i in range(len(coords)-1):
        cv2.circle(img, coords[i], 5, colors[i%3], 4)
        cv2.line(img, coords[i], coords[i+1], (0, 0, 255), thickness=4)
    cv2.line(img, coords[0], coords[-1], (0, 0, 255), thickness=4)


# Calculates tilt of QR code based on the top side.
# This is achieved by viewing the top side of the QR code as an (d_x, d_y) vector and
# finding the angle between it and a horizontal line (x axis) with inverse tangent.
def __calculateTilt(top_left_corner, top_right_corner):
    d_x = top_right_corner[0] - top_left_corner[0]
    d_y = top_right_corner[1] - top_left_corner[1]

    if d_x != 0:
        angle = atan(d_y / d_x)  # Radians
        angle *= 180 / pi  # Degrees
        return angle
    else:
        return CURRENT_TILT  # If d_x is 0 then an angle cannot be calculated. Return last known tilt angle.


# For debugging added a method that given the tilt of the QR code
# determines whether it was tilted to the left or the right and prints it to console.
# If the QR code was not tilted then nothing is printed to the console.
def printSignificantTilt(tilt, threshold=10):
    if tilt > threshold:
        print("LEFT")
    elif tilt < -threshold:
        print("RIGHT")

# Function continuously reads camera for frames and updates CURRENT_TILT and
# MOST_SIGNIFICANT_TILT based on the tilt of the QR code shown to the camera.
def __processVideoStreamThread(self):
    global CURRENT_TILT, MOST_SIGNIFICANT_TILT
    while 1:
        frame = __readFrame()
        coords = __getQRCodeCoordinates(frame)
        if len(coords) > 1:
            __drawROI(frame, coords)
            CURRENT_TILT = __calculateTilt(coords[0], coords[1])
            if abs(CURRENT_TILT) > abs(MOST_SIGNIFICANT_TILT):
                MOST_SIGNIFICANT_TILT = CURRENT_TILT

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        cv2.imshow(WINDOW_NAME, frame)

    cam.release()
    cv2.destroyAllWindows()

#######################
#                     #
#  PUBLIC FUNCTIONS  #
#                     #
#######################

# Returns the tilt angle of QR code that was last seen.
def getCurrentTilt():
    return CURRENT_TILT


# Returns the highest absolute tilt angle of QR code that
# was seen during video processing.
def getMostSignificantTilt():
    return MOST_SIGNIFICANT_TILT


# Sets the highest absolute tilt angle of QR code that
# was seen during video processing to 0.
def resetMostSignificantTilt():
    global MOST_SIGNIFICANT_TILT
    MOST_SIGNIFICANT_TILT = 0


# Starts the video processing thread that detects QR code shown to the user's camera
# and calculates the tilt of that QR code. Results of these calculations are stored
# in global variables CURRENT_TILT and MOST_SIGNIFICANT_TILT.
def init():
    video_processing_thread = threading.Thread(target=__processVideoStreamThread, args=(1,))
    video_processing_thread.start()

