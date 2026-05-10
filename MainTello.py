#!/usr/bin/env python3

# This is the main file to control the Tello drone

from djitellopy import tello
import time
import KeyboardTelloModule as kp
import cv2

img = None

def getKeyboardInput():
    #LEFT RIGHT, FRONT BACK, UP DOWN, YAW VELOCITY
    lr, fb, ud, yv = 0,0,0,0
    speed = 80
    liftSpeed = 80
    moveSpeed = 85
    rotationSpeed = 100
#Controls for the Left and Right movements
    if kp.getKey("LEFT"):
        lr = -speed 
    elif kp.getKey("RIGHT"):
        lr = speed
#Controls for the Front and Back movements
    if kp.getKey("UP"):
        fb = moveSpeed
    elif kp.getKey("DOWN"):
        fb = -moveSpeed
#Controls for the Up and Down movements
    if kp.getKey("w"):
        ud = liftSpeed
    elif kp.getKey("s"):
        ud = -liftSpeed
#Controls for drone rotation movements
    if kp.getKey("d"):
        yv = rotationSpeed
    elif kp.getKey("a"):
        yv = -rotationSpeed
#Controls for drone landing and takeoff
    if kp.getKey("q"):
        Drone.land(); time.sleep(3)
    elif kp.getKey("e"):
        Drone.takeoff()
#Screen capture images from camera
    if kp.getKey("z"):
        cv2.imwrite(f"tellopy/Resources/Images/{time.time()}.jpg", img)
        time.sleep(0.3)
#Return values that are given
    return [lr, fb, ud, yv]

#Initialize Keyboard Input
kp.init()

#Connect to the Tello Drone
Drone = tello.Tello()
Drone.connect()

#Get the current Battery Status
print(Drone.get_battery())

#Start the drone camera display stream
Drone.streamon()

while True:
#Get return values and store them within variables
    keyValues = getKeyboardInput()
    kp.update()
#Control the Tello drone
    Drone.send_rc_control(keyValues[0],keyValues[1],keyValues[2],keyValues[3])
#Get Frames from the Tello drone camera
    img = Drone.get_frame_read().frame
    img = cv2.resize(img, (1080,720))
#Show the frames on PC display
    cv2.imshow("DroneCapture", img)
    cv2.waitKey(1)