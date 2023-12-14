import numpy as np

from .calibration import config

def DLT(P1, P2, point1, point2):
    """
    See https://temugeb.github.io/opencv/python/2021/02/02/stereo-camera-calibration-and-triangulation.html
    for details on implementation
    """
 
    A = np.array([
        point1[1] * P1[2, :] - P1[1, :],
        P1[0, :] - point1[0] * P1[2, :],
        point2[1] * P2[2, :] - P2[1, :],
        P2[0, :] - point2[0] * P2[2, :]
    ])
 
    B = A.transpose() @ A
    U, s, Vh = np.linalg.svd(B, full_matrices = False)

    print(Vh[3,0:3]/Vh[3,3])
    return Vh[3,0:3]/Vh[3,3]

'''
Given two 2D (x,y) points from two cameras, triangulate the 3D position
'''
def triangulation(p1: np.ndarray, p2: np.ndarray) -> np.ndarray:
    K1 = np.array([[config.focal_length_x_1, 0, config.principal_point_x_1],
               [0, config.focal_length_y_1, config.principal_point_y_1],
               [0, 0, 1]])
    
    #Consider the primary camera as the world coordinate origin
    R1 = np.eye(3)
    T1 = [[0],[0],[0]]


    K2 = K2 = np.array([[config.focal_length_x_2, 0, config.principal_point_x_2],
               [0, config.focal_length_y_2, config.principal_point_y_2],
               [0, 0, 1]])
    R2= np.array(config.rvec_2)
    T2 = np.array([[config.X2], [config.Y2], [config.Z2]]) 

    RT1 = np.concatenate([R1, T1], axis = -1)
    P1 = K1 @ RT1

    RT2= np.concatenate([R2, T2], axis = -1)
    P2 = K2 @ RT2
    print(P1)

    DLT(P1, P2, p1, p2)



        