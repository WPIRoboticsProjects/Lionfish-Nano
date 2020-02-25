import cv2 as cv

cam = cv.VideoCapture(4)


cam2 = cv.VideoCapture(8)
print(cam.isOpened())
print(cam2.isOpened())

while True:
    ret, img1 = cam.read()
    ret1, img2 = cam2.read()

    if not ret:
        cv.imshow("img1", img1)
        cv.waitKey(1)
        cv.imshow("img2", img2)
        cv.waitKey(1)
