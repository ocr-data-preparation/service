import cv2
import numpy as np
from transform import four_point_transform
import imutils
import glob

#mencari titik berdasarkan template yang diberikan. lalu membetulkan perspective dari template tersebut
def template_match(template,image):
    img_rgb = cv2.imread(image)
    img_gray = cv2.cvtColor(img_rgb,cv2.COLOR_BGR2GRAY)
    template = cv2.imread(template,0)

    w,h = template.shape[::-1]
    print(w,h)
    res = cv2.matchTemplate(img_gray,template,cv2.TM_CCOEFF_NORMED)
    threshold = 0.48
    loc = np.where(res >= threshold)
    point_square = []
    for pt in zip(*loc[::-1]):
        point_square.append(pt)
        cv2.rectangle(img_rgb, pt, (pt[0] + w, pt[1] + h), (0,0,255), 2)
        print(pt)
    cv2.line(img_rgb,(point_square[0][0]+w,point_square[0][1]+h),(point_square[2][0]+w,point_square[2][1]),(0,0,255),2)
    cv2.line(img_rgb,(point_square[0][0]+w,point_square[0][1]+h),(point_square[1][0],point_square[1][1]+h),(0,0,255),2)
    cv2.line(img_rgb,(point_square[3][0],point_square[3][1]),(point_square[1][0],point_square[1][1]+h),(0,0,255),2)
    cv2.line(img_rgb,(point_square[3][0],point_square[3][1]),(point_square[2][0]+w,point_square[2][1]),(0,0,255),2)
    
    points = [[point_square[0][0]+w,point_square[0][1]+h],
                [point_square[1][0],point_square[1][1]+h],
                [point_square[2][0]+w,point_square[2][1]],
                [point_square[3][0],point_square[3][1]]
            ]
            
    warped = four_point_transform(img_rgb, np.array(points).reshape(4, 2))
    cv2.imwrite("transformed.jpeg",warped)

