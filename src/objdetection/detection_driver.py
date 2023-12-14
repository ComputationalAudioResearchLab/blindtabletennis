import numpy as np
from .clustering import get_centroid, cluster_weight_measure
from . import params
from typing import List
import os

class DetectionDriver():
    def __init__(self, mid_point: np.ndarray) -> None:
        self.centroid = np.array((-1, -1))
        self.ball: np.ndarray = None
        self.mid_point = mid_point

    def identify_ball(self, clusters: List[np.ndarray]) -> np.ndarray:
        if self.centroid[0] == -1 and self.centroid[1] == -1:
            return self.detect_ball(clusters)
        else:
            return self.track_ball(clusters)

    def track_ball(self, clusters: List[np.ndarray]):
        '''
        Method for detecting the ball based of stored previous position
        If the detected ball is outside a threshold to the previous position, 
        do no count it as the ball
        '''
        weight = float("inf")
        ball = None
        ball_centroid = None

        for cl in clusters:
            centroid = get_centroid(cl)

            diff = np.linalg.norm(self.centroid - centroid)

            # Must still check weight to avoid getting stuck tracking wrong cluster
            if diff < weight and cluster_weight_measure(cl, self.mid_point) < params.WEIGHT_THRESHOLD:
                weight = diff
                ball = cl
                ball_centroid = centroid

        if ball is None:
            self.cluster = None
            self.centroid = np.array((-1, -1))
            return None

        self.cluster = ball
        self.centroid = ball_centroid

        return self.centroid

    def detect_ball(self, clusters: List[np.ndarray]):
        '''
        Method for detecting based on weight and threshold whether the ball is in view
        Use when there is no previous tracking of ball ie: restarting ball tracking 
        '''

        weight = float("inf")
        ball = None
        ball_centroid = None

        for cl in clusters:

            centroid = get_centroid(cl)

            cur_weight = cluster_weight_measure(cl, self.mid_point)

            if cur_weight < weight and cur_weight < params.WEIGHT_THRESHOLD:
                weight = cur_weight
                ball = cl
                ball_centroid = centroid
        print(f"Chosen: Centroid: {ball_centroid}, midpoint: {self.mid_point} weight: {weight}")

        if ball is None:
            return None

        cluster_weight_measure(ball, self.mid_point)
        self.centroid = ball_centroid
        self.cluster = ball

        return self.centroid