import cv2
import threading
import time
from math import atan, pi

# Constants
WINDOW_NAME = "Camera view"

# Initialises user's camera and fetches QRCodeDetector class from cv2.
cam = cv2.VideoCapture(0)
qr_detector = cv2.QRCodeDetector()


# Reads frame from user's camera. Returns that frame (RGB).
def readFrame():
    _, frame = cam.read()
    return frame


# Find QR code coordinates from image.
# If there is NOT a QR code in image returns None
# If there IS a QR code in image returns coordinates of its corners like [(x0,y0),(x1,y1),(x2,y2),(x3,y3)]
def getQRCodeCoordinates(img):
    is_qr_shown, raw_coords = qr_detector.detect(img)
    if is_qr_shown:
        return processedCoords(raw_coords)
    else:
        return []


# Given raw coordinates like [[[x1, y1]], [[x2, y2]], ..., [[xn yn]]] returns coordinates like [(x0,y0),(x1,y1),(x2,y2), ..., (xn,yn)]
def processedCoords(raw_coordinates):
    processed = []
    for i in range(len(raw_coordinates[0])):
        coord = (int(raw_coordinates[0][i][0]), int(raw_coordinates[0][i][1]))
        processed.append(coord)
    return processed


# Draws a closed polygon on image based on coords.
def drawROI(img, coords):
    colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
    for i in range(len(coords)-1):
        cv2.circle(img, coords[i], 5, colors[i%3], 4)
        cv2.line(img, coords[i], coords[i+1], (0, 0, 255), thickness=4)
    cv2.line(img, coords[0], coords[-1], (0, 0, 255), thickness=4)


# Calculates tilt of QR code based on the top side.
# This is achieved by viewing the top side of the QR code as an (d_x, d_y) vector and
# finding the angle between it and x axis with inverse tangent.
def calculateTilt(top_left_corner, top_right_corner):
    d_x = top_right_corner[0] - top_left_corner[0]
    d_y = top_right_corner[1] - top_left_corner[1]

    angle = atan(d_y/d_x)    # Radians
    angle *= 180/pi          # Degrees
    return angle


# For debugging added a method that given the tilt of the QR code
# determines whether it was tilted to the left or the right and prints it to console.
# If the QR code was not tilted then nothing is printed to the console.
def printSignificantTilt(tilt, threshold=10):
    if (tilt > threshold):
        print("LEFT")
    elif (tilt < -threshold):
        print("RIGHT")


# Test how many frames can be read in a second.
# Jyrgen's laptop's webcam outputs ~30fps.
def __testFPS():
    while 1:
        start_time = time.perf_counter_ns()
        end_time = start_time

        fps = 0
        while end_time - start_time <= 1000000000:
            readFrame()
            fps += 1
            end_time = time.perf_counter_ns()
        print("end_time - start_time = ", end_time, "-", start_time, "=", end_time-start_time, "(ns)")
        print("FPS:", fps)


# Test how many frames can be processed in a second.
# On Jyrgen's laptop 50-80 frames could be processed in a second.
def __testQRDetectionPerformance():
    while 1:
        frames = []
        for _ in range(60):
            frames.append(readFrame())

        start_time = time.perf_counter_ns()
        for frame in frames:
            qr_detector.detect(frame)
        end_time = time.perf_counter_ns()

        print("end_time - start_time = ", end_time, "-", start_time, "=", end_time - start_time, "(ns)")
        print("QR detection fps:", len(frames) / ((end_time-start_time)/1000000000))


if __name__ == '__main__':
    #__testFPS()
    #__testQRDetectionPerformance()
    while 1:
        frame = readFrame()
        coords = getQRCodeCoordinates(frame)
        if len(coords) > 0:
            drawROI(frame, coords)
            print(coords)
            if len(coords) > 1:
                printSignificantTilt(calculateTilt(coords[0], coords[1]))

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        cv2.imshow(WINDOW_NAME, frame)

    cam.release()
    cv2.destroyAllWindows()

