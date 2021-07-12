'''
Library for basic video functions
'''

# Imports
import os
import cv2
import time
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm

# Main Functions
def SaveImageSeq(imgSeq, savePath, size=(640, 480), fps=24.0):
    imgSeq_PIL = []
    for frame in imgSeq:
        img = Image.fromarray((np.array(frame)*255).astype(np.uint8))
        imgSeq_PIL.append(img)

    if os.path.splitext(savePath)[-1] == '.gif':
        extraFrames = []
        if len(imgSeq_PIL) > 1:
            extraFrames = imgSeq_PIL[1:]
        imgSeq_PIL[0].save(savePath, save_all=True, append_images=extraFrames, format='GIF', loop=0, duration=len(imgSeq_PIL)/fps, optimize=True)
    else:
        out = cv2.VideoWriter(savePath, cv2.VideoWriter_fourcc(*'XVID'), fps, size)
        for frame in imgSeq:
            out.write(frame)
        out.release()

def DisplayImageSequence(imgSeq, delays, delayScale=0.1):
    delays = np.array(delays)
    delays_Norm = (delays - np.min(delays)) / (np.max(delays) - np.min(delays)) * delayScale
    frameNo = 0
    while(True):
        if delays_Norm[frameNo % len(imgSeq)] == 0.0 and ((frameNo % len(imgSeq)) < (len(imgSeq)-1)):
            frameNo += 1
            continue
        frame = imgSeq[frameNo % len(imgSeq)]
        cv2.imshow('Exec', frame)

        time.sleep(delays_Norm[frameNo % len(imgSeq)])

        # Press Q on keyboard to  exit
        if cv2.waitKey(25) & 0xFF == ord('q'):
            break

        frameNo += 1

def ViewImage(I):
    cv2.imshow('' ,I)
    cv2.waitKey(0)

# Driver Code