import cv2 as cv
import threading


def cam_thread(cam1, cam2):
    while True:
        val1, img1 = cam1.read()
        val2, img2 = cam2.read()
        cv.imshow("cam1", cv.pyrDown(img1))
        cv.imshow("cam2", cv.pyrDown(img2))
        if cv.waitKey(1) == 27:
            break

counter = 0
num_photos = 7
camera1 = "/dev/v4l/by-path/platform-70090000.xusb-usb-0:2.1:1.0-video-index0"
camera2 = "/dev/v4l/by-path/platform-70090000.xusb-usb-0:2.3:1.0-video-index0"

cam1 = cv.VideoCapture(camera1)
cam2 = cv.VideoCapture(camera2)
print("Camera: " + str(cam1.isOpened()))
print("Camera: " + str(cam2.isOpened()))

x = threading.Thread(target=cam_thread, args=[cam1, cam2])
x.start()
while counter < num_photos:
    input("Next image: ")
    val1, img1 = cam1.read()
    val2, img2 = cam2.read()
    name1 = "calibration_photos_stereo_water_test/left/" + str(counter) + ".png"
    name2 = "calibration_photos_stereo_water_test/right/" + str(counter) + ".png"
    cv.imwrite(name1, img1)
    cv.imwrite(name2, img2)
    print("Image " + str(counter) + " saved")
    counter += 1

cam1.release()
cam2.release()