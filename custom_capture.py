import cv2 as cv
import keyboard

num_photos = 20

camera = "/dev/v4l/by-path/platform-70090000.xusb-usb-0:2.1:1.0-video-index0"

cam = cv.VideoCapture(camera)
print("Camera: " + str(cam.isOpened()))

counter = 0

while counter < num_photos:
    val, img = cam.read()
    cv.imshow("cam", img)
    if cv.waitKey(1) == 27:
        break

    if keyboard.read_key() == "s":
        name = "./calibration_photos_water/left/" + str(counter) + ".png"
        cv.imwrite(name, img)
        print("Image " + str(counter) + " saved")
        counter += 1


cam.release()