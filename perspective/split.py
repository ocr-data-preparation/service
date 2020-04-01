import cv2
import imutils
image = cv2.imread("transformed.png")
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
gray = cv2.GaussianBlur(gray, (5, 5), 0)
edged = cv2.Canny(gray, 75, 200)
cnts = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
cnts = imutils.grab_contours(cnts)
cnts = sorted(cnts, key = cv2.contourArea, reverse = True)
squares = []
for c in cnts:
    peri = cv2.arcLength(c,True)
    approx = cv2.approxPolyDP(c, 0.02 * peri, True)
    if len(approx) == 4:
        squares.append(approx)


cv2.drawContours(image, squares, -1, (0, 255, 0), 2)
cv2.imshow("cnts",image)
cv2.waitKey(0)
cv2.destroyAllWindows()
cv2.imwrite("splitted.png",image)