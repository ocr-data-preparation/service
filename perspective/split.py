import cv2
import imutils
import scan
import numpy as np
kernel = np.ones((5,5),np.uint8)
# image = scan.parse_image("tes.png")
image = cv2.imread("transformed.png")
# ratio = image.shape[0]/500
# image = imutils.resize(image,height=500)
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
thresh = cv2.adaptiveThreshold(gray,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV,57,5)
# thresh = cv2.morphologyEx(thresh,cv2.MORPH_CLOSE,kernel)
cv2.imshow("cnts",imutils.resize(thresh.copy(),height=500))
cv2.waitKey(0)
cv2.destroyAllWindows()
# (thresh, bw) = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
# bw = cv2.morphologyEx(bw,cv2.MORPH_OPEN,kernel)

# gray = cv2.GaussianBlur(gray, (5, 5), 0)
# edged = cv2.Canny(gray, 75, 200)
cnts = cv2.findContours(thresh.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
cnts = imutils.grab_contours(cnts)
cnts = sorted(cnts, key = cv2.contourArea, reverse = True)
squares = []
f = open("tes.txt","w")
for c in cnts:
    peri = cv2.arcLength(c,True)
    approx = cv2.approxPolyDP(c, 0.01 * peri, True)
    if (len(approx) == 4 and  cv2.contourArea(approx)>cv2.contourArea(cnts[7])-0.5*cv2.contourArea(cnts[7]) and cv2.contourArea(approx)<cv2.contourArea(cnts[7])+0.5*cv2.contourArea(cnts[7]) ):
        f.write(str(cv2.contourArea(approx))+"\n")
        squares.append(approx)
for s in squares:
    cv2.drawContours(image,[s], -1, (0, 255, 0), 2)
# image = imutils.resize(image,height=int(500*ratio))
cv2.imshow("cnts",imutils.resize(image.copy(),height=500))
cv2.waitKey(0)
cv2.destroyAllWindows()
cv2.imwrite("splitted.png",image)
f.close()