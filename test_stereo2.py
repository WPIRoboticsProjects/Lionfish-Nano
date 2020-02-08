import cv2 as cv
import numpy as np
from stereovision.calibration import StereoCalibration

# Camera settimgs
cam_width = 1920
cam_height = 1080

# Final image capture settings
scale_ratio = 0.5

# Camera resolution height must be dividable by 16, and width by 32
cam_width = int((cam_width+31)/32)*32
cam_height = int((cam_height+15)/16)*16
print ("Used camera resolution: "+str(cam_width)+" x "+str(cam_height))

# Buffer for captured image settings
img_width = int (cam_width * scale_ratio)
img_height = int (cam_height * scale_ratio)
print ("Scaled image resolution: "+str(img_width)+" x "+str(img_height))

left_device = "/dev/v4l/by-path/platform-70090000.xusb-usb-0:2.1:1.0-video-index0"
right_device = "/dev/v4l/by-path/platform-70090000.xusb-usb-0:2.3:1.0-video-index0"
left = cv.VideoCapture(left_device)
right = cv.VideoCapture(right_device)

print("Left: " + str(left.isOpened()))
print("Right: " + str(right.isOpened()))

print('Read calibration data and rectifying stereo pair...')
calibration = StereoCalibration(input_folder='calib_result')


def remap_img(img, side):
    h, w = img.shape[:2]
    newcameramtx, roi = cv.getOptimalNewCameraMatrix(calibration.cam_mats[side], calibration.dist_coefs[side], (w,h), 1, (w,h))
    mapx, mapy = cv.initUndistortRectifyMap(calibration.cam_mats[side], calibration.dist_coefs[side], None, newcameramtx, (w,h), 5)
    dst = cv.remap(img, mapx, mapy, cv.INTER_LINEAR)

    #x,y,w,h = roi
    #dst = dst[y:y+h, x:x+w]
    return dst




sbm = cv.StereoBM_create(numDisparities=16, blockSize=9) # block size 9 seemed pretty good
while True:
    val, l_img = left.read()
    val2, r_img = right.read()

    l_img_resized = cv.resize(l_img, (img_width, img_height), interpolation = cv.INTER_AREA)
    r_img_resized = cv.resize(r_img, (img_width, img_height), interpolation = cv.INTER_AREA)

    l_img_gray = cv.cvtColor(l_img_resized, cv.COLOR_BGR2GRAY)
    r_img_gray = cv.cvtColor(r_img_resized, cv.COLOR_BGR2GRAY)



    l_remapped = remap_img(l_img_gray, "left")
    r_remapped = remap_img(r_img_gray, "right")
    #print(l_remapped.shape)
    #print(r_remapped.shape)
    disparity = sbm.compute(l_remapped, r_remapped)
    norm_img = cv.normalize(disparity, None, alpha=0, beta=1, norm_type=cv.NORM_MINMAX, dtype=cv.CV_32F)


    # TODO work on getting distance from center of image
    y_center = int(norm_img.shape[0]/2)
    x_center = int(norm_img.shape[1]/2)

    print(norm_img.item((y_center, x_center)))
    #depth = 29.7 / 

    #cv.imshow("left", l_img_gray)
    #cv.imshow("right", r_img_gray)
    #cv.imshow("left_remapped", l_remapped)
    #cv.imshow("right_remapped", r_remapped)
    #cv.imshow("disparity", disparity)
    cv.imshow("norm", norm_img)

    if cv.waitKey(1) == 27:
        break


left.release()
right.release()

























