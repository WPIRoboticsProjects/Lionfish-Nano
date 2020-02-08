import cv2 as cv
import time

num_photos = 31
countdown = 5
cam_width = 1920
cam_height = 1080
scale_ratio = 0.5

cam_width = int((cam_width+31)/32)*32
cam_height = int((cam_height+15)/16)*16
print ("Used camera resolution: "+str(cam_width)+" x "+str(cam_height))

img_width = int (cam_width * scale_ratio)
img_height = int (cam_height * scale_ratio)
print ("Scaled image resolution: "+str(img_width)+" x "+str(img_height))


left_device = "/dev/v4l/by-path/platform-70090000.xusb-usb-0:2.1:1.0-video-index0"
right_device = "/dev/v4l/by-path/platform-70090000.xusb-usb-0:2.3:1.0-video-index0"
left = cv.VideoCapture(left_device)
right = cv.VideoCapture(right_device)

print("Left: " + str(left.isOpened()))
print("Right: " + str(right.isOpened()))

counter = 0
while counter < num_photos:

    end_time = time.time() + countdown
    while time.time() < end_time:
        val, img1 = left.read()
        val2, img2 = right.read()
        cv.imshow("left", img1)
        cv.imshow("right", img2)
        if cv.waitKey(1) == 27:
            break

    val, l_img = left.read()
    val2, r_img = right.read()

    l_img_resized = cv.resize(l_img, (img_width, img_height), interpolation = cv.INTER_AREA)
    r_img_resized = cv.resize(r_img, (img_width, img_height), interpolation = cv.INTER_AREA)
    
    left_name = "./calibration_photos/left/" + str(counter-1) + ".png"
    right_name = "./calibration_photos/right/" + str(counter-1) + ".png"
    
    cv.imwrite(left_name, l_img_resized)
    cv.imwrite(right_name, r_img_resized)
    #cv.imwrite(left_name, l_img)
    #cv.imwrite(right_name, r_img)
    print("Image " + str(counter) + " saved")

    if cv.waitKey(1) == 27:
        break

    counter += 1

left.release()
right.release()
