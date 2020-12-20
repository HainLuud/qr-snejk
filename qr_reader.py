import cv2

# Initialises user's camera and fetches QRCodeDetector class from cv2.
cam = cv2.VideoCapture(0)
qr_detector = cv2.QRCodeDetector()

# Reads frame from user's camera. Returns that frame (RGB).
def readFrame():
    retval, frame = cam.read()
    return frame

# Find QR code coordinates from image.
# If there is NOT a QR code in image returns None
# If there IS a QR code in image returns coordinates of its corners like [(x0,y0),(x1,y1),(x2,y2),(x3,y3)]
def getQRCodeCoordinates(img):
    is_qr_shown, raw_coords = qr_detector.detect(img)
    if is_qr_shown:
        return processedCoords(raw_coords)
    else:
        return None

# Given raw coordinates like [[[x1, y1]], [[x2, y2]], ..., [[xn yn]]] returns coordinates like [(x0,y0),(x1,y1),(x2,y2), ..., (xn,yn)]
def processedCoords(raw_coordinates):
    processed = []
    for i in range(len(raw_coordinates)):
        coord = (int(raw_coordinates[i][0][0]), int(raw_coordinates[i][0][1]))
        processed.append(coord)
    return processed

# Draws a closed polygon on image based on coords.
def drawROI(img, coords):
    for i in range(len(coords)-1):
        cv2.line(img, coords[i], coords[i+1], (0, 0, 255), thickness=4)
    cv2.line(img, coords[0], coords[-1], (0, 0, 255), thickness=4)


if __name__ == '__main__':
    while 1:
        frame = readFrame()
        coords = getQRCodeCoordinates(frame)
        if coords is not None:
            drawROI(frame, coords)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        cv2.imshow('image', frame)

    cam.release()
    cv2.destroyAllWindows()

