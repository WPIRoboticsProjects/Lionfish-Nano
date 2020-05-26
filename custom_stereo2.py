import os
import numpy as np
import cv2 as cv
import glob

left_device = "/dev/v4l/by-path/platform-70090000.xusb-usb-0:2.1:1.0-video-index0"
right_device = "/dev/v4l/by-path/platform-70090000.xusb-usb-0:2.3:1.0-video-index0"

left = cv.VideoCapture(left_device)
right = cv.VideoCapture(right_device)

print("Left: " + str(left.isOpened()))
print("Right: " + str(right.isOpened()))

#---------------------------------------------------
# Calibration

criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)
objp = np.zeros((9*6,3), np.float32)
objp[:,:2] = np.mgrid[0:9,0:6].T.reshape(-1,2)

objpoints = [] # 3d point in real world space
imgpoints_l = [] # 2d points in image plane.
imgpoints_r = [] # 2d points in image plane.

directory = 'calibration_photos_stereo_test/left/'
directory2 = 'calibration_photos_stereo_test/right/'

for filename in os.listdir(directory):
    img_l = cv.imread(os.path.join(directory, filename))
    img_r = cv.imread(os.path.join(directory2, filename))

#for i in range(0, len(images_l)):
#    img_l = cv.imread(images_l.pop(i))
#    img_r = cv.imread(images_r.pop(i))
    gray_l = cv.cvtColor(img_l, cv.COLOR_BGR2GRAY)
    gray_r = cv.cvtColor(img_r, cv.COLOR_BGR2GRAY)

    # Find the chess board corners
    ret_l, corners_l = cv.findChessboardCorners(gray_l, (9, 6), None)
    ret_r, corners_r = cv.findChessboardCorners(gray_r, (9, 6), None)

    # If found, add object points, image points (after refining them)
    if ret_l and ret_r:
        objpoints.append(objp)

        corners2_l = cv.cornerSubPix(gray_l, corners_l, (11, 11), (-1, -1), criteria)
        corners2_r = cv.cornerSubPix(gray_r, corners_r, (11, 11), (-1, -1), criteria)
        imgpoints_l.append(corners2_l)
        imgpoints_r.append(corners2_r)

        # Draw and display the corners
        img_l_show = cv.drawChessboardCorners(img_l, (9,6), corners2_l,ret_l)
        img_r_show = cv.drawChessboardCorners(img_r, (9, 6), corners2_r, ret_r)
        #cv.imshow('img_l', img_l_show)
        #cv.imshow('img_r', img_r_show)
        #cv.waitKey(2000)

cv.destroyAllWindows()


cameraMatrixLeft = np.zeros( (3,3) )
cameraMatrixRight = np.zeros( (3,3) )
distortionLeft = np.zeros( (8,1) )
distortionRight = np.zeros( (8,1) )
height, width = cv.pyrDown(img_l).shape[:2]

rms, leftMatrix, leftDistortion, rightMatrix, rightDistortion, R, T, E, F = cv.stereoCalibrate(objpoints, imgpoints_l, imgpoints_r,  cameraMatrixLeft, distortionLeft, cameraMatrixRight, distortionRight, (width, height),criteria, flags=0)

leftRectTransform, rightRectTransform, leftProjMatrix, rightProjMatrix, _, _, _ = cv.stereoRectify(leftMatrix, leftDistortion, rightMatrix, rightDistortion,  (width, height), R, T, alpha=-1)
leftMapX, leftMapY = cv.initUndistortRectifyMap(leftMatrix, leftDistortion, leftRectTransform, leftProjMatrix, (width, height), cv.CV_32FC1)
rightMapX, rightMapY = cv.initUndistortRectifyMap(rightMatrix, rightDistortion, rightRectTransform, rightProjMatrix, (width, height), cv.CV_32FC1)

#----------------------------------------------------
# show disparity

# best out of water calibration
stereo = cv.StereoSGBM_create(
   minDisparity = 0, #min_disp
   numDisparities = 128, #112, #128, #num_disp,
   blockSize = 1, #1, #5, #7, #9, # 16
   P1 = 10, #100, #8*3*window_size**2,
   P2 = 200, #800, #960, #32*3*window_size**2,
   disp12MaxDiff = 5, #60, #83, #30, #7, #10, #1,
   uniquenessRatio = 0, #3, #10,
   speckleWindowSize = 20, #100,
   speckleRange = 5 #9 #32
)
# need to calibrate for water

while True:
    val, l_img = left.read()
    val2, r_img = right.read()
    if cv.waitKey(1) == 27:
        break
    imgL = cv.pyrDown(l_img)
    imgR = cv.pyrDown(r_img)

    frameLeftNew = cv.cvtColor(imgL, cv.COLOR_BGR2GRAY)
    frameRightNew = cv.cvtColor(imgR, cv.COLOR_BGR2GRAY)

    leftRectified = cv.remap(frameLeftNew, leftMapX, leftMapY, cv.INTER_LINEAR)
    rightRectified = cv.remap(frameRightNew, rightMapX, rightMapY, cv.INTER_LINEAR)

    disparity = stereo.compute(leftRectified, rightRectified).astype(np.float32) / 16.0

    # cv.filterSpeckles(disparity, 0, 6000, 96)
    # cv.imshow("Normalized Disparity", (disparity / 16.0 - 0) / 96);
    #print(disparity.shape)
    disparity = (disparity-0) / 128
    out_val = disparity[120,240]
    print(out_val)
    # focal length = 2.97 mm
    # baseline = 437 mm 

    # (xmin,ymin),(xmax,ymax)
    xmin = 235 #160 + 80 - 5
    xmax = 245 #xmin + 10
    ymin = 115 #120 - 5
    ymax = 125 # ymin + 10
    cv.rectangle(disparity, (xmin,ymin),(xmax,ymax), (255,255,255))
    # cv.imshow("Normalized Disparity", (disparity / 16.0 - 0) / 128)
    cv.imshow("Normalized Disparity", disparity)

left.release()
right.release()
