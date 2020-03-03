import flask
import os
from datetime import datetime
from werkzeug.utils import secure_filename

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