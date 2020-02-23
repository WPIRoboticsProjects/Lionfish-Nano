import cv2 as cv
import threading
import keyboard

class KeyboardThread(threading.Thread):

    def __init__(self, input_cbk = None, name='keyboard-input-thread'):
        self.input_cbk = input_cbk
        super(KeyboardThread, self).__init__(name=name)
        self.start()

    def run(self):
        while True:
            self.input_cbk(input()) #waits to get input + Return

def my_callback(inp):
    while True:
        val, img = cam.read()
        cv.imshow("cam", img)
        if cv.waitKey(1) == 27:
            break

counter = 0
num_photos = 20
camera = "/dev/v4l/by-path/platform-70090000.xusb-usb-0:2.1:1.0-video-index0"

cam = cv.VideoCapture(camera)
print("Camera: " + str(cam.isOpened()))

kthread = KeyboardThread(my_callback)
while counter < num_photos:
    input("Next image: ")
    val, img = cam.read()
    name = "./calibration_photos_water/left/" + str(counter) + ".png"
    cv.imwrite(name, img)
    print("Image " + str(counter) + " saved")
    counter += 1

cam.release()