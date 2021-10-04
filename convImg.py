# -*- coding: utf-8 -*-
"""
Created on Mon Dec  3 12:06:21 2018

@author: lhuismans
"""
import PIL 
import numpy as np

def convertBinary(adress):
    with PIL.Image.open(adress) as imageFile:
        f = imageFile.convert('L')
        imgArr = np.asarray(f).ravel()
        #Making the image binary:
        imgArr = (imgArr > 0)*1 #First part makes it True/False, multiplying by 1 converts it to binary
    return imgArr

imgSeq = convertBinary("DMDpictures\halfonDMD.png")
print(imgSeq.size)