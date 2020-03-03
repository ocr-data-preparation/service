import flask
import os
from datetime import datetime
from werkzeug.utils import secure_filename
from __future__ import division
from PIL import Image
import math


def saveImage(image):
    current_time = datetime.now().strftime("%d-%b-%Y (%H:%M:%S)")
    filename = secure_filename(current_time)

    path = os.path.join("images/", filename + ".jpg")
    image.save(path)




def image_slicer(image_path,  outdir):
    """slice an image into parts slice_size tall"""
    img = Image.open(image_path)
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
            
            #save the slice
            working_slice.save(os.path.join(outdir + "\\" + str(x+1), str(x)+str(y)+".png"))
            
            count +=1
            left += slice_size_horz

        upper += slice_size_vert