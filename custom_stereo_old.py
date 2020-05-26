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
objp_l = np.zeros((9*6,3), np.float32)
objp_l[:,:2] = np.mgrid[0:9,0:6].T.reshape(-1,2)
objp_r = np.zeros((9*6,3), np.float32)
objp_r[:,:2] = np.mgrid[0:9,0:6].T.reshape(-1,2)

objpoints_l = [] # 3d point in real world space
imgpoints_l = [] # 2d points in image plane.
objpoints_r = [] # 3d point in real world space
imgpoints_r = [] # 2d points in image plane.

images = glob.glob('calibration_photos_test/left/*.png')

for fname in images:
    img = cv.imread(fname)
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

    # Find the chess board corners
    ret, corners = cv.findChessboardCorners(gray, (9, 6), None)

    # If found, add object points, image points (after refining them)
    if ret == True:
        objpoints_l.append(objp_l)

        corners2 = cv.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
        imgpoints_l.append(corners2)

        # Draw and display the corners
        img = cv.drawChessboardCorners(img, (9,6), corners2,ret)
        # cv.imshow('img', img)
        #cv.waitKey(500)

cv.destroyAllWindows()
ret, mtx, dist, rvecs, tvecs = cv.calibrateCamera(objpoints_l, imgpoints_l, gray.shape[::-1],None,None)
l_val, l_img = left.read()
h,  w = cv.pyrDown(l_img).shape[:2]
newcameramtx_l, roi_l = cv.getOptimalNewCameraMatrix(mtx,dist,(w,h),1,(w,h))
# undistort
mapx_l,mapy_l = cv.initUndistortRectifyMap(mtx,dist,None,newcameramtx_l,(w,h),5)
# dst = cv.remap(l_img,mapx,mapy,cv.INTER_LINEAR)

images = glob.glob('calibration_photos_test/right/*.png')

for fname in images:
    img = cv.imread(fname)
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

    # Find the chess board corners
    ret, corners = cv.findChessboardCorners(gray, (9, 6), None)

    # If found, add object points, image points (after refining them)
    if ret == True:
        objpoints_r.append(objp_r)

        corners2 = cv.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
        imgpoints_r.append(corners2)

        # Draw and display the corners
        img = cv.drawChessboardCorners(img, (9,6), corners2,ret)
        # cv.imshow('img', img)
        #cv.waitKey(500)

cv.destroyAllWindows()
ret, mtx, dist, rvecs, tvecs = cv.calibrateCamera(objpoints_r, imgpoints_r, gray.shape[::-1],None,None)

r_val, r_img = right.read()
h,  w = cv.pyrDown(r_img).shape[:2]
newcameramtx_r, roi_r = cv.getOptimalNewCameraMatrix(mtx,dist,(w,h),1,(w,h))
# undistort
mapx_r, mapy_r = cv.initUndistortRectifyMap(mtx,dist,None,newcameramtx_r,(w,h),5)
# dst = cv.remap(l_img,mapx,mapy,cv.INTER_LINEAR)

#----------------------------------------------------
# show disparity


#window_size = 25#4
#min_disp = 0#16 #32#-64 #16
#num_disp = 112-min_disp
#num_disp = 128-min_disp
#num_disp = 144-min_disp
#stereo = cv.StereoSGBM_create(
#    minDisparity = 0, #min_disp
#    numDisparities = 96, #128, #num_disp,
#    blockSize = 5, #1, #5, #7, #9, # 16
#    P1 = 0, #8*3*window_size**2,
#    P2 = 0, #960, #32*3*window_size**2,
#    disp12MaxDiff = 83, #30, #7, #10, #1,
#    uniquenessRatio = 0, #10,
#    speckleWindowSize = 0, #100,
#    speckleRange = 0 #9 #32
#)


stereo = cv.StereoSGBM_create(
    minDisparity = 0, #min_disp
    numDisparities = 96, #128, #num_disp,
    blockSize = 1, #1, #5, #7, #9, # 16
    P1 = 100, #8*3*window_size**2,
    P2 = 800, #960, #32*3*window_size**2,
    disp12MaxDiff = 60, #83, #30, #7, #10, #1,
    uniquenessRatio = 0, #3, #10,
    speckleWindowSize = 0, #100,
    speckleRange = 0 #9 #32
)


while True:
    val, l_img = left.read()
    val2, r_img = right.read()
    if cv.waitKey(1) == 27:
        break
    imgL = cv.pyrDown(l_img)
    imgR = cv.pyrDown(r_img)

    frameLeftNew = cv.cvtColor(imgL, cv.COLOR_BGR2GRAY)
    frameRightNew = cv.cvtColor(imgR, cv.COLOR_BGR2GRAY)

    dst_l = cv.remap(frameLeftNew, mapx_l, mapy_l, cv.INTER_LINEAR)
    dst_r = cv.remap(frameRightNew, mapx_r, mapy_r, cv.INTER_LINEAR)

    disparity = stereo.compute(dst_l, dst_r).astype(np.float32) / 16.0


    # cv.imshow("Normalized Disparity", (disparity / 16.0 - 0) / 128)
    cv.imshow("Normalized Disparity", (disparity - 0) / 128)



left.release()
right.release()
