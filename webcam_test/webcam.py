"""
WEBCAM FACIAL RECOGNITION TEST

Uses CV3 or higher. Im using

    pip install opencv-python

Code Source: https://github.com/shantnu/Webcam-Face-Detect/

To Run:

    Python webcam.py

To Quit:

    hit the 'q' key

TO DO:
-up framerate
-lip detecting and point plotting
-capture video for later use (and audio?)
"""

import cv2
import os
import sys
import logging as log
import datetime as dt
from time import sleep

dir = os.path.realpath(__file__)
casc = "Mouth.xml"

cascPath = os.path.join(os.path.split(dir)[0], casc)

faceCascade = cv2.CascadeClassifier(cascPath)

# log.basicConfig(filename='webcam.log',level=log.INFO)

# anterior = 0

video_capture = cv2.VideoCapture(0)

while True:
    if cv2.waitKey(1) & 0xFF == ord('q'): #quit if q pressed
        break

    ret, frame = video_capture.read() #capture frame-by-frame

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = faceCascade.detectMultiScale(
        gray,
        scaleFactor=1.7,
        minNeighbors=12,
        minSize=(50,50)
    )

    roi = frame
    offset = 50

    for (x, y, h, w) in faces:

        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2) #creating green rectangle
        roi = frame[y-offset:y+h+offset, x-offset:x+w+offset]

    # if anterior != len(faces):
    #     anterior = len(faces)
    #     log.info("faces: "+str(len(faces))+" at "+str(dt.datetime.now()))

    # Display the resulting frame
    cv2.imshow('ROI', roi)
    cv2.imshow('Video', frame)

# When everything is done, release the capture
video_capture.release()
cv2.destroyAllWindows()
