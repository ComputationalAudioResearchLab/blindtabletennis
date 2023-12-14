import cv2
import numpy as np
from typing import List
import PIL.Image


def calibrate(images: List[PIL.Image.Image]):
	# Defining the dimensions of checkerboard
	CHECKERBOARD = (5,9)
	WORLD_SCALING = 1
	criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
	

	objpoints = []
	imgpoints = [] 
	
	
	# Defining the world coordinates for 3D points
	objp = np.zeros((1, CHECKERBOARD[0] * CHECKERBOARD[1], 3), np.float32)

	objp[0,:,:2] = np.mgrid[0:CHECKERBOARD[0], 0:CHECKERBOARD[1]].T.reshape(-1, 2)

	chess_flags = (cv2.CALIB_CB_ADAPTIVE_THRESH | cv2.CALIB_CB_NORMALIZE_IMAGE)

	for im in images:

		pil_image = im.convert('RGB') 
		open_cv_image = np.array(pil_image) 
		# Convert RGB to BGR 
		img = open_cv_image[:, :, ::-1].copy() 
		gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)


		# Find the chess board corners
		# If desired number of corners are found in the image then ret = true
		ret, corners = cv2.findChessboardCorners(gray, CHECKERBOARD, chess_flags)

		"""
		If desired number of corner are detected,
		we refine the pixel coordinates and display 
		them on the images of checker board
		"""
		if ret == True:
			print("Found!")
			objpoints.append(objp)
			# refining pixel coordinates for given 2d points.
			corners2 = cv2.cornerSubPix(gray, corners, (11,11),(-1,-1), criteria)
			
			imgpoints.append(corners2)

			# Draw and display the corners
			img = cv2.drawChessboardCorners(img, CHECKERBOARD, corners2, ret)
		
		cv2.imshow('img',img)
		cv2.waitKey(10)
		

	if(len(objpoints) == 0):
		print("could not detect pattern")
		return None
	
	"""
	Performing camera calibration by 
	passing the value of known 3D points (objpoints)
	and corresponding pixel coordinates of the 
	detected corners (imgpoints)
	"""
	ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)
	print("Ret: ")
	print(ret)
	print("Camera matrix : \n")
	print(mtx)
	print("dist : \n")
	print(dist)
	print("rvecs : \n")
	print(rvecs)
	print("tvecs : \n")
	print(tvecs)
	return ret, mtx, dist, rvecs, tvecs



