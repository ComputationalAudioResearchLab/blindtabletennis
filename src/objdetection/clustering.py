from sklearn.cluster import DBSCAN
import numpy as np
from . import params


def clustering_dbscan(events: np.ndarray):

    clusterer = DBSCAN(eps=15, min_samples=50)
    clusterer.fit(events)

    retrieved_clusters = set(clusterer.labels_)
    #Remove noise
    if -1 in retrieved_clusters:
        retrieved_clusters.remove(-1)

    clusters = []

    for label in iter(retrieved_clusters):
        labelled_events = np.column_stack((events, clusterer.labels_))

        # This array contains all of indexes of (x,y) locations for a single cluster
        detected_pixel_indexes = np.where(labelled_events[:, 2] == label)

        # Now use the locations determined above to store the actual (x,y) values
        detected_pixels = labelled_events[detected_pixel_indexes]

        # Add all the (x,y) values for each cluster to a list
        clusters.append(detected_pixels[:, 0:2])

    return clusters


def get_centroid(cluster: np.ndarray) -> np.ndarray:

    # Calculate the mean of all the points in the cluster for X and Y directions.
    # This will provide the centroid of the cluster.

    meanX = int(np.mean(cluster[:, 0]))
    meanY = int(np.mean(cluster[:, 1]))

    return np.array((meanX, meanY))


def cluster_weight_measure(cluster: np.ndarray, mid_point: np.ndarray) -> float:
    ''' 
    @param cluster: the cluster of points forming a potention feature
    @param mid_point: the mid point of the frame denoting the approximate table centre
    @return: A float weight measure. Smaller weight means more likely to be the ball 
    
    '''

    # TO DO more measures
    max_xy = np.max(cluster, axis=0)
    min_xy = np.min(cluster, axis=0)

    area_est = (max_xy[0] - min_xy[0]) * (max_xy[1] - min_xy[1])
    area_weight = area_est/params.CLUSTER_AREA_THRESHOLD

    density_weight = area_est/cluster.size

    max_dist = np.linalg.norm(mid_point - np.array((0, 0)))
    diff = np.linalg.norm(mid_point - get_centroid(cluster))
    dist_weight = diff/max_dist

    # print(
    #     f"area {area_est}, area_weight: {area_weight}, density_weight {density_weight}, diff {diff}, dist_weight {dist_weight}, size {cluster.size}")
    return density_weight + dist_weight + area_weight

def weight_cluster_speaker(cluster):
    max_xy = np.max(cluster, axis=0)
    min_xy = np.min(cluster, axis=0)

    area_est = (max_xy[0] - min_xy[0]) * (max_xy[1] - min_xy[1])
    area_weight = area_est/params.SPEAKER_AREA_THRESHOLD

    density_weight = area_est/cluster.size

    return density_weight + area_weight

def get_speaker_clusters(clusters):
    weight = float("inf")
    cluster_centre = None

    for cl in clusters:
        print(f"Cluster with {cl.size} events")
        centroid = get_centroid(cl)

        cur_weight = weight_cluster_speaker(cl)

        if cur_weight < weight and cur_weight < params.WEIGHT_THRESHOLD:
            weight = cur_weight
            cluster_centre = centroid
    print(f"Chosen: Centroid: {cluster_centre},  weight: {weight}")
    
    return cluster_centre


# [-7.54705005  0.59644436  7.65888463]

# [-3.12273554  0.79054129  3.10630408]