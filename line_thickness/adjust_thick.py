import cv2
import numpy as np
# dilation memperbanyak putih pada objek
# erotion memperbanyak hitam pada objek
def adjust_thick(img,thickness,tipe):
    image = cv2.imread(img)
    kernel = np.ones((thickness),np.uint8)
    if (tipe == "erosion"):
        result = cv2.erode(image,kernel,iterations=1)
    elif (tipe == "dilation"):
        result = cv2.dilate(img,kernel,iterations=1)
    return result
# img = cv2.imread("angka.png",0)
# kernel = np.ones((5,5),np.uint8)
# erosion = cv2.erode(img,kernel,iterations=1)
# dilation = cv2.dilate(img,kernel,iterations=1)
# cv2.imshow('erosion',erosion)
# cv2.imshow('dilation',dilation)
# cv2.waitKey(0)
# cv2.destroyAllWindows()