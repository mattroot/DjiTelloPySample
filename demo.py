# UI demo

# external libs
import cv2
import numpy as np

# get image, desaturize and detect lines
disp = cv2.imread("picture.jpg")
# image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
# ret, detected = cv2.threshold(image, 50, 255, cv2.THRESH_BINARY_INV)

# create a color copy for pretty view
# disp = cv2.cvtColor(detected, cv2.COLOR_GRAY2BGR)

# create HUD - stage 1
cv2.rectangle(disp, (0, 240), (960, 480), (0, 255, 0), 2)
cv2.rectangle(disp, (360, 0), (600, 720), (0, 0, 255), 2)

# create HUD - stage 2
cv2.putText(disp, f'Battery: 0%', (30, 30), cv2.FONT_HERSHEY_COMPLEX, 1.0, (255, 255, 255))
cv2.putText(disp, f'State: DroneState.DetectCenter', (30, 60), cv2.FONT_HERSHEY_COMPLEX, 1.0, (255, 255, 255))

# show view
cv2.imshow('Tello feed', disp)
cv2.waitKey(0)

# when finished with main lopp
cv2.destroyAllWindows()
