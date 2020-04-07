# belum dijadiin kelas jadi belum bisa di pake buat ke server
from actions.transform import four_point_transform
from skimage.filters import threshold_local
import numpy as np
import argparse
import cv2
import imutils


#fungsi membaca sebuah image lalu menggelapkannya untuk mendapatkan silhout garis dari image 
# lalu membetulkan prespective image setelah silhout digunakan
def parse_image(img):
	if(isinstance(img,str)):
		image = cv2.imread(img)
	else:
		image = img
	ratio = image.shape[0] / 500.0
	orig = image.copy()
	image = imutils.resize(image, height = 500)

	gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
	gray = cv2.GaussianBlur(gray, (5, 5), 0)
	edged = cv2.Canny(gray, 75, 200)

	cnts = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
	cnts = imutils.grab_contours(cnts)
	cnts = sorted(cnts, key = cv2.contourArea, reverse = True)[:5]

	for c in cnts:
		peri = cv2.arcLength(c, True)
		approx = cv2.approxPolyDP(c, 0.02 * peri, True)
		if len(approx) == 4:
			screenCnt = approx
			break


	if(screenCnt is not None):
		warped = four_point_transform(orig, screenCnt.reshape(4, 2) * ratio)
		#ngenulis ke file baru yang namanya transformed.jpeg
		#cv2.imwrite("images/temp/transformed.jpeg",warped)
		return warped
