import cv2
import numpy as np
from typing import List
import PIL.Image

def pil_to_cv(img):
    pil_image = img.convert('RGB') 
    open_cv_image = np.array(pil_image) 
    img_cv = open_cv_image[:, :, ::-1].copy() 
    return img_cv
    
    

def stereo_calibrate(primary_images: List[PIL.Image.Image], 
                     secondary_images: List[PIL.Image.Image]):
 
    #change this if stereo calibration not good.
    CHECKERBOARD = (5,9)
    WORLD_SCALING = 10.2 #cdm

    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
 
    # Defining the world coordinates for 3D points
    objp = np.zeros((1, CHECKERBOARD[0] * CHECKERBOARD[1], 3), np.float32)
    objp[0,:,:2] = np.mgrid[0:CHECKERBOARD[0], 0:CHECKERBOARD[1]].T.reshape(-1, 2)
    objp = objp * WORLD_SCALING
    
    WIDTH  = primary_images[0].size[0]
    HEIGHT = primary_images[0].size[1]

 
    #Pixel coordinates of checkerboards
    imgpoints_primary = [] #
    imgpoints_secondary = []
 
    #coordinates of the checkerboard in checkerboard world space.
    objpoints = [] # 3d point in real world space
    chess_flags = (cv2.CALIB_CB_ADAPTIVE_THRESH | cv2.CALIB_CB_NORMALIZE_IMAGE)
 
    for frame1, frame2 in zip(primary_images, secondary_images):
        img1 =pil_to_cv(frame1)
        img2 =pil_to_cv(frame2)
        gray1 = cv2.cvtColor(img1,cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
        
        c_ret1, corners1 = cv2.findChessboardCorners(gray1, CHECKERBOARD, chess_flags)
        c_ret2, corners2 = cv2.findChessboardCorners(gray2, CHECKERBOARD, chess_flags)
 
        if c_ret1 == True and c_ret2 == True:
            corners1 = cv2.cornerSubPix(gray1, corners1, (11, 11), (-1, -1), criteria)
            corners2 = cv2.cornerSubPix(gray2, corners2, (11, 11), (-1, -1), criteria)
 
            img1 = cv2.drawChessboardCorners(img1, CHECKERBOARD, corners1, c_ret1)
 
 
            img2 = cv2.drawChessboardCorners(img2, CHECKERBOARD, corners2, c_ret2)
   
 
            objpoints.append(objp)
            imgpoints_primary.append(corners1)
            imgpoints_secondary.append(corners2)

        concatenated_image = np.hstack([img1, img2])
        cv2.imshow('Calibration image',concatenated_image)
        cv2.waitKey(0)
    

    if len(objpoints) == 0:
        print("could not detect pattern")
        raise ValueError("Failed to calibrate")
    
    ret1, cameraMatrix1, distCoeffs1, rvecs1, tvecs1 = cv2.calibrateCamera(objpoints, imgpoints_primary, gray1.shape[::-1], None, None)
    ret2, cameraMatrix2, distCoeffs2, rvecs2, tvecs2 = cv2.calibrateCamera(objpoints, imgpoints_secondary, gray2.shape[::-1], None, None)
    print("Ret1: ", ret1)
    print("Ret2: ", ret2)

    ret, mtx1, dist1, mtx2, dist2, R, T, E, F = cv2.stereoCalibrate(objpoints, imgpoints_primary, imgpoints_secondary, 
                                                                    cameraMatrix1, distCoeffs1, cameraMatrix2, distCoeffs2, (WIDTH, HEIGHT), criteria = criteria)
 
    print("Ret: ", ret)
    return R, T, mtx1, mtx2