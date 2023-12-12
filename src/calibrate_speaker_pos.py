import numpy as np
from objdetection.clustering import clustering_dbscan, get_speaker_clusters
from objdetection.position_estimation import triangulation

from objdetection.eventprocessing.event_stream_reader import EventStreamReaderOffline
from objdetection.visualise import visualise_single

print("Starting calibration")

filename_1 = "/Users/carlab/Documents/Phoebe_thesis/blindpingpong/src/calibration_images/speaker_primary/2023-11-22T08-07-35.772043Z_00050421_primary.es"
filename_2 = "/Users/carlab/Documents/Phoebe_thesis/blindpingpong/src/calibration_images/speaker_secondary/2023-11-22T08-07-35.772043Z_00050423_secondary.es"

buffer_1 = EventStreamReaderOffline(filename_1)
buffer_2 = EventStreamReaderOffline(filename_2)

def get_speaker_pos(buffer):
    chunk = buffer.get_chunk()

    if chunk is None:
        return

    events = np.column_stack((chunk['x'], chunk['y']))

    clusters = clustering_dbscan(events)
    pos = get_speaker_clusters(clusters)

    visualise_single( np.column_stack((chunk['x'], chunk['y'], chunk['on'])), 720, 1280, pos)
    return pos



print("Camera 1 staring")
pos1 = get_speaker_pos(buffer_1)

print("Camera 2 staring")
pos2 = get_speaker_pos(buffer_2)

est = triangulation(pos1, pos2)
print("Estimate: ", est)