import cv2 as cv
import os

from stereovision.calibration import StereoCalibrator
from stereovision.calibration import StereoCalibration
from stereovision.calibration import ChessboardNotFoundError

total_photos = 30
img_width = 960
img_height = 544
image_size = (img_width, img_height)


rows = 7 #8
columns = 7 # 8
square_size = 4.445 #1.75

calibrator = StereoCalibrator(rows, columns, square_size, image_size)
photo_counter = 0

while photo_counter != total_photos:
    print("image: " + str(photo_counter))
    photo_counter += 1
    left_name = "calibration_photos/left/" + str(photo_counter) + ".png"
    right_name = "calibration_photos/left/" + str(photo_counter) + ".png"

    if os.path.isfile(left_name) and os.path.isfile(right_name):
        img_l = cv.imread(left_name, 1)
        img_r = cv.imread(right_name, 1)
        try:
            calibrator._get_corners(img_l)
            calibrator._get_corners(img_r)
            
        except ChessboardNotFoundError as error:
            print(error)
        else:
           calibrator.add_corners((img_l,img_r), True)



print ('Starting calibration... It can take several minutes!')
calibration = calibrator.calibrate_cameras()
calibration.export('calib_result')
print ('Calibration complete!')

calibration = StereoCalibration(input_folder='calib_result')
rectified_pair = calibration.rectify((img_l, img_r))


cv.imshow('Left CALIBRATED', rectified_pair[0])
cv.imshow('Right CALIBRATED', rectified_pair[1])
cv.imwrite("rectifyed_left.jpg",rectified_pair[0])
cv.imwrite("rectifyed_right.jpg",rectified_pair[1])
cv.waitKey(0)
