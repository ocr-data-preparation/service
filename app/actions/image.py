from __future__ import division
import flask
import os
from datetime import datetime
from werkzeug.utils import secure_filename
from PIL import Image
import math
from random import seed
from random import randint

import cv2 as cv
import numpy as np
from matplotlib import pyplot as plt
import time
import os

def saveImage(image):
    current_time = datetime.now().strftime("%d-%b-%Y (%H:%M:%S)")
    filename = secure_filename(current_time)

    path = os.path.join("images/", filename + ".jpg")
    image.save(path)

def isBlank(image):
    img = cv.imread(image,0)
    _,th = cv.threshold(img,0,255,cv.THRESH_BINARY+cv.THRESH_OTSU)
    count0 = cv.countNonZero(th)
    countTotal = th.shape[0] * th.shape[1]
    white_percentage = count0/countTotal
    if white_percentage > 0.95:
        return True
    else:
        return False




def image_slicer(image,  outdir,current_time):
    """slice an image into parts slice_size tall"""

    path = os.path.join("app/actions/images/temp.jpg")
    print("yooo" + os.getcwd())
    image.save(path)
    #C:\Users\rizal\Documents\AllProject\ocr-data-preparation-service\app\actions\images

    #img = Image.open(image_path)
    img = Image.open(path)
    width, height = img.size

    
    upper = height/50
    left = width/50
    left_default = width/50
    slice_size_vert = (height - upper*2)/10
    slice_size_horz = (width - upper*2)/10

    slices = 10

    count = 1
    for x in range(slices):
        #if we are at the end, set the lower bound to be the bottom of the image
        left = left_default


        for y in range(slices):
            
            #set the bounding box! The important bit     
            bbox = (left, upper, left +slice_size_horz, upper + slice_size_vert)
            working_slice = img.crop(bbox)
            #left += slice_size_horz
            
            seed(1)


            name =       str(x)+str(y)+ "-"+ str(randint(1,100))
            #save the slice
            working_slice.save(os.path.join(outdir + "\\app\\result"+"\\"  + str(x+1), name + ".png"))
            
            count +=1
            left += slice_size_horz

        upper += slice_size_vert