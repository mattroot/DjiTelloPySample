import cv2
import numpy as np
from djitellopy import Tello
import time
import keyboard
from enum import Enum

class DroneState(Enum):
    DetectCenter = 0
    FollowLine = 1
    DetectNextLine = 2

def detection_condition(x, y, averages):
    return ((averages[x, y] / np.max(averages) < 2) and (averages[x, y] / np.max(averages) > 0.7))

def color_in(x, y, averages):
    return averages[x, y] > 30

fly = True

drone_state = DroneState.DetectCenter
line_x = 0
line_y = 0
fly_speed = 10

t = Tello()
t.connect()
print(t.get_battery())
t.streamon()
time.sleep(1)

t.takeoff()
t.move_up(130)

while fly:
    img = t.get_frame_read().frame

    if keyboard.is_pressed('space'):
        fly = False

    # converted = convert_hls(img)
    image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret, detected = cv2.threshold(image, 50, 255, cv2.THRESH_BINARY_INV)
    disp = cv2.cvtColor(detected, cv2.COLOR_GRAY2BGR)

    cv2.rectangle(disp, (0, 240), (960, 480), (0, 255, 0), 2)
    cv2.rectangle(disp, (360, 0), (600, 720), (0, 0, 255), 2)

    target_rect   = detected[240:480, 360:600]

    left_target   = detected[240:480, 0:360]
    right_target  = detected[240:480, 600:960]
    top_target    = detected[0:240, 360:600]
    bottom_target = detected[480:720, 360:600]

    top_left      = detected[0:240, 0:360]
    top_right     = detected[0:240, 600:960]
    bottom_left   = detected[480:720, 0:360]
    bottom_right  = detected[480:720, 600:960]

    averages = np.array([
        [np.mean(top_left),    np.mean(top_target),    np.mean(top_right)],
        [np.mean(left_target), np.mean(target_rect),   np.mean(right_target)],
        [np.mean(bottom_left), np.mean(bottom_target), np.mean(bottom_right)]
    ])

    if drone_state == DroneState.DetectCenter:
        if not detection_condition(1, 1, averages):
            # top target
            if detection_condition(0, 1, averages):
                t.send_rc_control(0, 0, fly_speed, 0)

            # bottom target
            if detection_condition(2, 1, averages):
                t.send_rc_control(0, 0, -fly_speed, 0)

            # left target
            if detection_condition(1, 0, averages):
                t.send_rc_control(-fly_speed, 0, 0, 0)

            # right target
            if detection_condition(2, 0, averages):
                t.send_rc_control(fly_speed, 0, 0, 0)

            # top left
            if detection_condition(0, 0, averages):
                t.send_rc_control(-fly_speed, 0, fly_speed, 0)

            # top right
            if detection_condition(0, 2, averages):
                t.send_rc_control(fly_speed, 0, fly_speed, 0)

            # bottom left
            if detection_condition(2, 0, averages):
                t.send_rc_control(-fly_speed, 0, -fly_speed, 0)

            # bottom right
            if detection_condition(2, 2, averages):
                t.send_rc_control(fly_speed, 0, -fly_speed, 0)

        else:
            t.send_rc_control(0, 0, 0, 0)
            drone_state = DroneState.DetectNextLine

    elif drone_state == DroneState.FollowLine:
        if detection_condition(line_x, line_y, averages):
            t.send_rc_control((line_y - 1) * fly_speed, 0, (line_x - 1) * -fly_speed, 0)
        else:
            t.send_rc_control(0, 0, 0, 0)
            drone_state = DroneState.DetectNextLine

    elif drone_state == DroneState.DetectNextLine:
        line_x = -1
        line_y = -1
        for x in (1, 2):
            for y in (0, 1, 2):
                if (x, y) == (1, 1): pass
                if detection_condition(x, y, averages):
                    line_x = x
                    line_y = y
                    drone_state = DroneState.FollowLine
                    break
            if line_x != -1 and line_y != -1: break
        if line_x == -1 and line_y == -1:
            drone_state = DroneState.DetectCenter

    cv2.putText(disp, f'Battery: {t.get_battery()}%', (30, 30), cv2.FONT_HERSHEY_COMPLEX, 1.0, (255, 255, 255))
    cv2.putText(disp, f'State: {drone_state}', (30, 60), cv2.FONT_HERSHEY_COMPLEX, 1.0, (255, 255, 255))
    print(averages)
    cv2.imshow('Tello feed', disp)
    cv2.waitKey(1)

cv2.destroyAllWindows()
t.land()

# yes = t.get_frame_read().frame
# image = cv2.cvtColor(yes, cv2.COLOR_BGR2GRAY)
# ret, detected = cv2.threshold(image,50, 255, cv2.THRESH_BINARY_INV)
# cv2.imwrite("picture.jpg", detected)

