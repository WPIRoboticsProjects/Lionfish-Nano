import cv2 as cv
import numpy as np
import json
from stereovision.calibration import StereoCalibrator
from stereovision.calibration import StereoCalibration

# Depth map default preset
SWS = 5
PFS = 5
PFC = 29
MDS = -30
NOD = 160
TTH = 100
UR = 10
SR = 14
SPWS = 100

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

#cv.namedWindow("Image")
#cv.moveWindow("Image", 50,100)
#cv.namedWindow("left")
#cv.moveWindow("left", 450,100)
#cv.namedWindow("right")
#cv.moveWindow("right", 850,100)

disparity = np.zeros((img_width, img_height), np.uint8)
sbm = cv.StereoBM_create(numDisparities=16, blockSize=9)  #(numDisparities=0, blockSize=21)

def stereo_depth_map(rectified_pair):
    dmLeft = rectified_pair[0]
    dmRight = rectified_pair[1]
    disparity = sbm.compute(dmLeft, dmRight)
    local_max = disparity.max()
    local_min = disparity.min()
    disparity_grayscale = (disparity-local_min)*(65535.0/(local_max-local_min))
    disparity_fixtype = cv.convertScaleAbs(disparity_grayscale, alpha=(255.0/65535.0))
    disparity_color = cv.applyColorMap(disparity_fixtype, cv.COLORMAP_JET)
    cv.imshow("Image", disparity_color)
    key = cv.waitKey(1) & 0xFF   
    if key == ord("q"):
        quit();
    return disparity_color




def load_map_settings( fName ):
    global SWS, PFS, PFC, MDS, NOD, TTH, UR, SR, SPWS, loading_settings
    print('Loading parameters from file...')
    f=open(fName, 'r')
    data = json.load(f)
    SWS=data['SADWindowSize']
    PFS=data['preFilterSize']
    PFC=data['preFilterCap']
    MDS=data['minDisparity']
    NOD=data['numberOfDisparities']
    TTH=data['textureThreshold']
    UR=data['uniquenessRatio']
    SR=data['speckleRange']
    SPWS=data['speckleWindowSize']    
    #sbm.setSADWindowSize(SWS)
    sbm.setPreFilterType(1)
    sbm.setPreFilterSize(PFS)
    sbm.setPreFilterCap(PFC)
    sbm.setMinDisparity(MDS)
    sbm.setNumDisparities(NOD)
    sbm.setTextureThreshold(TTH)
    sbm.setUniquenessRatio(UR)
    sbm.setSpeckleRange(SR)
    sbm.setSpeckleWindowSize(SPWS)
    f.close()
    print ('Parameters loaded from file '+fName)

load_map_settings ("3dmap_set.txt")


while True:
    val, l_img = left.read()
    val2, r_img = right.read()

    l_img_resized = cv.resize(l_img, (img_width, img_height), interpolation = cv.INTER_AREA)
    r_img_resized = cv.resize(r_img, (img_width, img_height), interpolation = cv.INTER_AREA)

    l_img_resized = cv.cvtColor(l_img_resized, cv.COLOR_BGR2GRAY)
    r_img_resized = cv.cvtColor(r_img_resized, cv.COLOR_BGR2GRAY)

    rectified_pair = calibration.rectify((l_img_resized, r_img_resized))
    disparity = sbm.compute(rectified_pair[0], rectified_pair[1])

    local_max = disparity.max()
    local_min = disparity.min()
    print("max: " + str(local_max) + " min: " + str(local_min))

    cv.imshow("disp", disparity)
    #disparity = stereo_depth_map(rectified_pair)

    #cv.imshow("left", l_img_resized)
    #cv.imshow("right", r_img_resized)

    if cv.waitKey(1) == 27:
        break


left.release()
right.release()

