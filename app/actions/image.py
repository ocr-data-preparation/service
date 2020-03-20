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

def save_image(image):
    current_time = datetime.now().strftime("%d-%b-%Y (%H:%M:%S)")
    filename = secure_filename(current_time)

    path = os.path.join("images/", filename + ".jpg")
    image.save(path)

    return path

def is_blank(image):
    path = save_image(image)
    img = cv.imread(path,0)
    _,th = cv.threshold(img,0,255,cv.THRESH_BINARY+cv.THRESH_OTSU)
    count0 = cv.countNonZero(th)
    countTotal = th.shape[0] * th.shape[1]
    white_percentage = count0/countTotal

    if white_percentage > 0.95:
        return True
    else:
        return False

def slice_image(image):
    path = save_image(image)

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
        left = left_default

        for y in range(slices): 
            bbox = (left, upper, left +slice_size_horz, upper + slice_size_vert)
            working_slice = img.crop(bbox)
            
            current_time = datetime.now().strftime(str(y) + " - %d-%b-%Y (%H:%M:%S)")
            filename = secure_filename(current_time)
            working_path = os.path.join("images/"+ str((x+1)%10) +"/", filename + ".jpg")

            working_slice.save(working_path)
            
            count +=1
            left += slice_size_horz

        upper += slice_size_vert

        
#resize image: tambahin ke tempat ingin dipakai
def resize(x):
    # Opens a image in RGB mode  
    im = Image.open(r"file[ath")  
  
    newsize = (x, x) 
    im1 = im1.resize(newsize) 
    # Shows the image in image viewer  
    im1.show()  

