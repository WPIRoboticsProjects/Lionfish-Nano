import cv2 as cv

cam_width = 1920
cam_height = 1080
scale_ratio = 0.5

cam_width = int((cam_width+31)/32)*32
cam_height = int((cam_height+15)/16)*16

img_width = int (cam_width * scale_ratio)
img_height = int (cam_height * scale_ratio)

left_device = "/dev/v4l/by-path/platform-70090000.xusb-usb-0:2.1:1.0-video-index0"
right_device = "/dev/v4l/by-path/platform-70090000.xusb-usb-0:2.3:1.0-video-index0"
left = cv.VideoCapture(left_device)
right = cv.VideoCapture(right_device)

print("Left: " + str(left.isOpened()))
print("Right: " + str(right.isOpened()))

val, l_img = left.read()
val2, r_img = right.read()

l_img_resized = cv.resize(l_img, (img_width, img_height), interpolation = cv.INTER_AREA)
r_img_resized = cv.resize(r_img, (img_width, img_height), interpolation = cv.INTER_AREA)

left_name = "./test_photos/left.png"
right_name = "./test_photos/right.png"

cv.imwrite(left_name, l_img_resized)
cv.imwrite(right_name, r_img_resized)
