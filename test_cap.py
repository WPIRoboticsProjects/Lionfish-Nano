import cv2 as cv
import threading


def cam_thread(cam_l, cam_r):
    while True:
        val, img1 = cam_l.read()
        cv.imshow("cam", cv.pyrDown(img1))
        val2, img2 = cam_r.read()
        cv.imshow("cam2", cv.pyrDown(img2))
        if cv.waitKey(1) == 27:
            break

l_camera = "/dev/v4l/by-path/platform-70090000.xusb-usb-0:2.1:1.0-video-index0"
r_camera = "/dev/v4l/by-path/platform-70090000.xusb-usb-0:2.3:1.0-video-index0"

cam_l = cv.VideoCapture(l_camera)
cam_r = cv.VideoCapture(r_camera)

print("Camera: " + str(cam_l.isOpened()))
print("Camera: " + str(cam_r.isOpened()))

x = threading.Thread(target=cam_thread, args=[cam_l, cam_r])
x.start()

input("capture image: ")
val, img_l = cam_l.read()
val2, img_r = cam_r.read()

cv.imwrite("left_img_s.png", cv.pyrDown(img_l))
cv.imwrite("right_img_s.png", cv.pyrDown(img_r))

cam_l.release()
cam_r.release()
