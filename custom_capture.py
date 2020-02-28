import cv2 as cv
from multiprocessing import Process, Queue


def cam_thread(cam1, cam2, cam1_queue, cam2_queue):
    while True:
        val1, img1 = cam1.read()
        val2, img2 = cam2.read()
        cam1_queue.put(img1)
        cam2_queue.put(img2)
        cv.imshow("cam1", cv.pyrDown(img1))
        cv.imshow("cam2", cv.pyrDown(img2))
        if cv.waitKey(10) == 27:
            break

counter = 0
num_photos = 7
camera1 = "/dev/v4l/by-path/platform-70090000.xusb-usb-0:2.1:1.0-video-index0"
camera2 = "/dev/v4l/by-path/platform-70090000.xusb-usb-0:2.3:1.0-video-index0"

cam1 = cv.VideoCapture(camera1)
cam2 = cv.VideoCapture(camera2)
print("Camera: " + str(cam1.isOpened()))
print("Camera: " + str(cam2.isOpened()))

cam1_queue = Queue()
cam2_queue = Queue()

x = Process(target=cam_thread, args=(cam1, cam2, cam1_queue, cam2_queue,))
x.start()
while counter < num_photos:
    input("Next image: ")

    if not cam1_queue.empty() and not cam2_queue.empty():
        for i in range(cam1_queue.qsize()):
            img1 = cam1_queue.get()
        for j in range(cam2_queue.qsize()):
            img2 = cam2_queue.get()
    #val1, img1 = cam1.read()
    #val2, img2 = cam2.read()
        name1 = "calibration_photos_stereo_water_test/left/" + str(counter) + ".png"
        name2 = "calibration_photos_stereo_water_test/right/" + str(counter) + ".png"
        cv.imwrite(name1, img1)
        cv.imwrite(name2, img2)
        print("Image " + str(counter) + " saved")
        counter += 1

cam1.release()
cam2.release()
