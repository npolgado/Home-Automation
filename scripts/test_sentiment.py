import cv2
import os
import numpy as np
import time
import pandas as pd
from keras.models import load_model

def main():
    """
    loading the keras model
    """
    print("----------------------------")
    print("----------------------------")
    model = load_model('model.h5')
    print("----------------------------")
 
    #loading cascade classifier for detecting facial feature
    face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
    cap = cv2.VideoCapture(0)
    #declaring a list to store emotions
    emotions = ['angry','disgust','fear','happy','sad','surprise','neutral']
    while True:
        ret, frame = cap.read()
        if ret:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)
            #checking if faces are detected
            if faces:
                #print(faces)
                #print(faces.shape[0])
                for (x,y,w,h) in faces:
                    print("----------------------------")
                    #extracting the detected faces from the frame
                    detected_face = frame[int(y):int(y+h), int(x):int(x+w)]
                    detected_face = cv2.cvtColor(detected_face, cv2.COLOR_BGR2GRAY)
                    detected_face = cv2.resize(detected_face, (48,48))
                    img_pixels = np.asarray(detected_face)
                    img_pixels = img_pixels.astype('float32')
                    img_pixels /= 255
                    img_pixels = np.expand_dims(img_pixels, axis=0)
                    img_pixels = np.expand_dims(img_pixels,-1)
                    #performing the prediction with the trained model
                    predictions = model.predict(img_pixels)
                    #print(predictions)
                    max_index = np.argmax(predictions[0])
                    emotions_detected = emotions[max_index]
                    #print(emotions_detected)
                    #print(np.max(predictions[0]))
                    font = cv2.FONT_HERSHEY_SIMPLEX
                    cv2.putText(frame, emotions_detected, (int(x), int(y)), font, 1, (255,255,0), 2)
                    cv2.rectangle(frame, (x,y), (x+w,y+h), (255,0,0), 2)
            #resizing the frame for performance
            frame = cv2.resize(frame, (400,300))
            cv2.imshow('Facial Emotion Recognition', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        else:
            print('error')
            break
    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()