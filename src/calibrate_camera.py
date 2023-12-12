import numpy as np
from objdetection.calibration.intrinsic_calibration import calibrate
from objdetection.calibration.stereo_calibration import stereo_calibrate
from objdetection.calibration.calib_images_helper import create_calib_images

WIDTH = 1280
HEIGHT = 720

dirname = "/Volumes/T7/Calibration_data/"
# dirname = "/Users/carlab/Documents/Phoebe_thesis/blindpingpong/src/calibration_images/"

print("creating primary images")
primary_images = create_calib_images(dirname + "primary/")
print("creating secondary images")
secondary_images = create_calib_images(dirname + "secondary/")

print("Stereo calibration")

R, T, mtx1, mtx2 = stereo_calibrate(primary_images, secondary_images)

print("Rotation: ")
print(R)
print("Translation")
print(T)
print("Matrix 1")
print(mtx1)
print("Matrix 2")
print(mtx2)

config_str = f""" 
WIDTH = {primary_images[0].size[0]}
HEIGHT = {primary_images[0].size[1]}

#Camera 1 calibration
focal_length_x_1 = {mtx1[0][0]}
focal_length_y_1 = {mtx1[1][1]}
principal_point_x_1 = {mtx1[0][2]}
principal_point_y_1 = {mtx1[1][2]}

#Camera 2 Calibration

focal_length_x_2 = {mtx2[0][0]}
focal_length_y_2 = {mtx2[1][1]}
principal_point_x_2 = {mtx2[0][2]}
principal_point_y_2 = {mtx2[1][2]}
rvec_2 = {R.tolist()}
X2 = {T.flatten()[0]}
Y2 = {T.flatten()[1]}
Z2 = {T.flatten()[2]}
"""
# Write to config file

with open("objdetection/calibration/config.py", "w") as file:
	file.write(config_str)