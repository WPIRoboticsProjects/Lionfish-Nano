import cv2 as cv
import numpy as np
import os

total_photos = 20
img_width = 960
img_height = 544
image_size = (img_width, img_height)


rows = 7 #8
columns = 7 # 8
square_size = 44.45 #4.445 #1.75

img_points_l = []
img_points_r = []
obj_points = []

objp = np.zeros((np.prod((rows,columns)), 3), np.float32)
objp[:, :2] = np.indices((rows, columns)).T.reshape(-1,2)
objp *= square_size

criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 100, 1e-5)
flags = (cv.CALIB_FIX_ASPECT_RATIO + cv.CALIB_ZERO_TANGENT_DIST + cv.CALIB_SAME_FOCAL_LENGTH)

cam_mats_l = None
cam_mats_r = None
dist_coef_l = None
dist_coef_r = None
rot_mat = None
trans_vec = None
e_mat = None
f_mat = None

rect_trans_l = None
rect_trans_r = None
proj_mats_l = None
proj_mats_r = None
disp_to_depth_map = None
valid_boxes_l = None
valid_boxes_r = None

def remap_img(img, side):
    h, w = img.shape[:2]
    print(h)
    print(w)
    if side == "left":
        #newcameramtx, roi = cv.getOptimalNewCameraMatrix(cam_mats_l, dist_coef_l, (w,h), 1, (w,h))
        #mapx, mapy = cv.initUndistortRectifyMap(cam_mats_l, dist_coef_l, None, newcameramtx, (w,h), 5)
        dst = cv.remap(img, mapx_l, mapy_l, cv.INTER_LINEAR)
    else:
        #newcameramtx, roi = cv.getOptimalNewCameraMatrix(cam_mats_r, dist_coef_r, (w,h), 1, (w,h))
        #mapx, mapy = cv.initUndistortRectifyMap(cam_mats_r, dist_coef_r, None, newcameramtx, (w,h), 5)
        dst = cv.remap(img, mapx_r, mapy_r, cv.INTER_LINEAR)
    
    #dst = cv.remap(img, mapx, mapy, cv.INTER_LINEAR)
    #dst = cv.remap(img, calibration.undistortion_map[side], calibration.rectification_map[side], cv.INTER_NEAREST)

    #x,y,w,h = roi
    #dst = dst[y:y+h, x:x+w]
    return dst

#--------------------------------------------------------------------
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
#----------------------------------------------------------------------

photo_counter = 0
while photo_counter != total_photos:
    print("image: " + str(photo_counter))
    photo_counter += 1
    left_name = "calibration_photos/left/" + str(photo_counter) + ".png"
    right_name = "calibration_photos/left/" + str(photo_counter) + ".png"

    if os.path.isfile(left_name) and os.path.isfile(right_name):
        img_l = cv.imread(left_name, 1)
        img_r = cv.imread(right_name, 1)
        img_l_gray = cv.cvtColor(img_l, cv.COLOR_BGR2GRAY)
        img_r_gray = cv.cvtColor(img_r, cv.COLOR_BGR2GRAY)

        ret_l, corners_l = cv.findChessboardCorners(img_l_gray, (rows, columns))
        ret_r, corners_r = cv.findChessboardCorners(img_r_gray, (rows, columns))
        if ret_l and ret_r:
            obj_points.append(objp)
            cv.cornerSubPix(img_l_gray, corners_l, (11,11), (-1,-1), (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001))
            cv.cornerSubPix(img_r_gray, corners_r, (11,11), (-1,-1), (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001))
            img_points_l.append(corners_l)
            img_points_r.append(corners_r)
        else:
            print("Chessboard " + str(photo_counter) + " not found")

print("stereo cal")
cam_matx_l = np.zeros((3,3))
cam_matx_r = np.zeros((3,3))
dist_l = np.zeros((8,1))
dist_r = np.zeros((8,1))
(cam_mats_l, dist_coef_l, cam_mats_r, dist_coef_r, rot_mat, trans_vec, e_mat, f_mat) = cv.stereoCalibrate(obj_points, img_points_l, img_points_r, cam_matx_l, dist_l, cam_matx_r, dist_r, image_size, flags=0)[1:]

print("cam mats l")
print(cam_mats_l)
print("cam mats r")
print(cam_mats_r)
print("dist coef l")
print(dist_coef_l)
print("dist coef r")
print(dist_coef_r)
print("image size")
print(image_size)
print("R")
print(rot_mat)
print("trans")
print(trans_vec)

print("stereo rectify")
rect_trans_l, rect_trans_r, proj_mats_l, proj_mats_r, _,_,_ = cv.stereoRectify(cameraMatrix1=cam_mats_l, distCoeffs1=dist_coef_l, cameraMatrix2=cam_mats_r, distCoeffs2=dist_coef_r, imageSize=image_size, R=rot_mat, T=trans_vec, alpha=0)

print("undistort maps")
mapx_l, mapy_l = cv.initUndistortRectifyMap(cam_mats_l, dist_coef_l, rect_trans_l, proj_mats_l, image_size, cv.CV_32FC1)
mapx_r, mapy_r = cv.initUndistortRectifyMap(cam_mats_r, dist_coef_r, rect_trans_r, proj_mats_r, image_size, cv.CV_32FC1)

print("start capture")
window_size = 4
min_disp = 32#-64 #16
num_disp = 112-min_disp
stereo = cv.StereoSGBM_create(minDisparity = min_disp,
    numDisparities = num_disp,
    blockSize = 9, # 16
    P1 = 8*3*window_size**2,
    P2 = 32*3*window_size**2,
    disp12MaxDiff = 1,
    uniquenessRatio = 10,
    speckleWindowSize = 100,
    speckleRange = 32
)
while True:
    val, l_img = left.read()
    val2, r_img = right.read()

    if cv.waitKey(1) == 27:
        break

    l_img_resized = cv.resize(l_img, (img_width, img_height), interpolation = cv.INTER_AREA)
    r_img_resized = cv.resize(r_img, (img_width, img_height), interpolation = cv.INTER_AREA)

    l_img_gray = cv.cvtColor(l_img_resized, cv.COLOR_BGR2GRAY)
    r_img_gray = cv.cvtColor(r_img_resized, cv.COLOR_BGR2GRAY)



    l_remapped = cv.remap(l_img_gray, mapx_l, mapy_l, cv.INTER_LINEAR)
    r_remapped = cv.remap(r_img_gray, mapx_r, mapy_r, cv.INTER_LINEAR)

    imgL = cv.pyrDown(l_remapped)   #cv.imread(cv.samples.findFile('aloeL.jpg')))  # downscale images for faster processing
    imgR = cv.pyrDown(r_remapped)

    disp = stereo.compute(imgL, imgR)
    norm_img = cv.normalize(disp, None, alpha=0, beta=1, norm_type=cv.NORM_MINMAX, dtype=cv.CV_32F)


    # TODO work on getting distance from center of image
    #y_center = int(norm_img.shape[0]/2)
    #x_center = int(norm_img.shape[1]/2)

    #print(norm_img.item((y_center, x_center)))
    #depth = 29.7 / 

    #cv.imshow("left", l_img_gray)
    #cv.imshow("right", r_img_gray)
    cv.imshow("left_remapped", l_remapped)
    cv.imshow("right_remapped", r_remapped)
    #cv.imshow("disparity", disparity)
    cv.imshow("norm", norm_img)
    cv.imshow('disparity', (disp-min_disp)/num_disp)

    


left.release()
right.release()















