import numpy as np
import cv2 as cv

ply_header = '''ply
format ascii 1.0
element vertex %(vert_num)d
property float x
property float y
property float z
property uchar red
property uchar green
property uchar blue
end_header
'''

def write_ply(fn, verts, colors):
    verts = verts.reshape(-1, 3)
    colors = colors.reshape(-1, 3)
    verts = np.hstack([verts, colors])
    with open(fn, 'wb') as f:
        f.write((ply_header % dict(vert_num=len(verts))).encode('utf-8'))
        np.savetxt(f, verts, fmt='%f %f %f %d %d %d ')

left_device = "/dev/v4l/by-path/platform-70090000.xusb-usb-0:2.1:1.0-video-index0"
right_device = "/dev/v4l/by-path/platform-70090000.xusb-usb-0:2.3:1.0-video-index0"
left = cv.VideoCapture(left_device)
right = cv.VideoCapture(right_device)

# disparity range is tuned for 'aloe' image pair
#window_size = 3
#min_disp = 32 #16
#num_disp = 112-min_disp
#stereo = cv.StereoSGBM_create(minDisparity = min_disp,
#    numDisparities = num_disp,
#    blockSize = 12, # 16
#    P1 = 8*3*window_size**2,
#    P2 = 32*3*window_size**2,
#    disp12MaxDiff = 1,
#    uniquenessRatio = 10,
#    speckleWindowSize = 100,
#    speckleRange = 32
#)

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

def main():
    while True:
        val, l_img = left.read()
        val2, r_img = right.read()
        if cv.waitKey(1) == 27:
            exit()
        imgL = cv.pyrDown(l_img)   #cv.imread(cv.samples.findFile('aloeL.jpg')))  # downscale images for faster processing
        imgR = cv.pyrDown(r_img)   #cv.imread(cv.samples.findFile('aloeR.jpg')))

        disp = stereo.compute(imgL, imgR).astype(np.float32) / 16.0

    #print('generating 3d point cloud...',)
    #h, w = imgL.shape[:2]
    #f = 0.8*w                          # guess for focal length
    #Q = np.float32([[1, 0, 0, -0.5*w],
    #                [0,-1, 0,  0.5*h], # turn points 180 deg around x-axis,
    #                [0, 0, 0,     -f], # so that y-axis looks up
    #                [0, 0, 1,      0]])
    #points = cv.reprojectImageTo3D(disp, Q)
    #colors = cv.cvtColor(imgL, cv.COLOR_BGR2RGB)
    #mask = disp > disp.min()
    #out_points = points[mask]
    #out_colors = colors[mask]
    #out_fn = 'out.ply'
    #write_ply(out_fn, out_points, out_colors)
    #print('%s saved' % out_fn)

        cv.imshow('left', imgL)
        cv.imshow('right', imgR)
        cv.imshow('disparity', (disp-min_disp)/num_disp)

        y_center = int(norm_img.shape[0]/2)
        x_center = int(norm_img.shape[1]/2)

        print(norm_img.item((y_center, x_center)))
        #depth = 29.7 / 


if __name__ == '__main__':
    print(__doc__)
    main()
    cv.destroyAllWindows()
