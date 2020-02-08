import cv2 as cv
import numpy as np
import json
from stereovision.calibration import StereoCalibrator
from stereovision.calibration import StereoCalibration
from matplotlib import pyplot as plt



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
#calibration = StereoCalibration(input_folder='calib_result')
sbm = cv.StereoBM_create(numDisparities=16, blockSize=15)


while True:
    val, l_img = left.read()
    val2, r_img = right.read()

    #l_img_resized = cv.resize(l_img, (img_width, img_height), interpolation = cv.INTER_AREA)
    #r_img_resized = cv.resize(r_img, (img_width, img_height), interpolation = cv.INTER_AREA)

    #l_img_resized = cv.cvtColor(l_img_resized, cv.COLOR_BGR2GRAY)
    #r_img_resized = cv.cvtColor(r_img_resized, cv.COLOR_BGR2GRAY)

    l_img_gray = cv.cvtColor(l_img, cv.COLOR_BGR2GRAY)
    r_img_gray = cv.cvtColor(r_img, cv.COLOR_BGR2GRAY)


    disparity = sbm.compute(l_img_gray, r_img_gray)
    norm_img = cv.normalize(disparity, None, alpha=0, beta=1, norm_type=cv.NORM_MINMAX, dtype=cv.CV_32F)
    cv.imshow("Disp", disparity)
    cv.imshow("Norm", norm_img)
    
    #rectified_pair = calibration.rectify((l_img_resized, r_img_resized))
    #stereo_depth_map(rectified_pair)

    #disparity = sbm.compute(rectified_pair[0], rectified_pair[1])
    #local_max = disparity.max()
    #local_min = disparity.min()
    #print("Max: " +  str(local_max) + " Min: " + str(local_min))
    #disparity_grayscale = (disparity-local_min)*(65535.0/(local_max-local_min))
    #disparity_fixtype = cv.convertScaleAbs(disparity_grayscale, alpha=(255.0/65535.0))
    #disparity_color = cv.applyColorMap(disparity_fixtype, cv.COLORMAP_JET)
    #cv.imshow("Image", disparity_color)
    #key = cv.waitKey(1) & 0xFF   
    #if key == ord("q"):
    #    quit();

    #cv.imshow("Image", disparity_color)

    cv.imshow("left", l_img_gray)
    cv.imshow("right", r_img_gray)

    if cv.waitKey(1) == 27:
        break


left.release()
right.release()



















