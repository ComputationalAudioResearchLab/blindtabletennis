from collections import deque
import threading
import os
import time
from objdetection.detection_driver import DetectionDriver
from objdetection.clustering import clustering_dbscan, get_centroid
from objdetection.eventprocessing.event_stream_reader import EventStreamReaderOffline
import numpy as np
import vispy.app
from display.display_interface import Canvas
from objdetection.visualise import visualise_single

from objdetection.position_estimation import triangulation

REFERENCE = time.monotonic()
exit_event = threading.Event()


def thread_camera1(driver: DetectionDriver, event_stream: EventStreamReaderOffline, pos_deque: deque, events_deque: deque):
    print("Camera 1 thread staring")
    while not exit_event.is_set():

        chunk = event_stream.get_chunk()
        if chunk is None:
            print("Camera stream1 terminated")
            break

        if len(chunk) == 0:
            print("No events in chunk")
            continue

        events_deque.append(chunk)
        time.sleep(0.1)

        events = np.column_stack((chunk['x'], chunk['y']))

        clusters = clustering_dbscan(events)
        position = driver.detect_ball(clusters)
        pos_deque.append(position)

        # visualise_single(np.column_stack((chunk['x'], chunk['y'], chunk['on'])), 720, 1280, None)

        # now = time.monotonic()
        # delay = (REFERENCE + chunk["t"][-1]/1e6) - now 
        
        # if delay > 0:
        #     print("primary " ,delay)
        #     time.sleep(delay)
        



def thread_camera2(driver: DetectionDriver, event_stream: EventStreamReaderOffline, pos_deque: deque, events_deque: deque):
    print("Camera 2 thread staring")
    while not exit_event.is_set():
        chunk = event_stream.get_chunk()
        if chunk is None:
            print("camera 2 stream terminated")
            break

        events_deque.append(chunk)
        time.sleep(0.1)
        events = np.column_stack((chunk['x'], chunk['y']))

        clusters = clustering_dbscan(events)
        position = driver.detect_ball(clusters)
        pos_deque.append(position)

        # now = time.monotonic()
        # delay =(REFERENCE + chunk["t"][-1]/1e6) - now
        # if delay > 0:
        #     print("secondary: " + delay)
        #     time.sleep(delay)


def user_input_thread():
    while True:
        user_input = input("Enter 'exit' to terminate the program: \n")
        if user_input.lower() == 'exit':
            exit_event.set()
            break

def triangulate_thread(camera_1_deque, camera_2_deque):
    print("Starting triangulate Thread")
    while not exit_event.is_set():
        if len(camera_1_deque) > 0 and len(camera_2_deque) > 0:
            pos1 = camera_1_deque.popleft()
            pos2 = camera_2_deque.popleft()
            if (pos1 is None or pos2 is None):
                print("Ball not found", pos1, pos2)
                continue
            estimation = triangulation(pos1, pos2)
            print(estimation)



result_update_1 = threading.Event()
result_update_2 = threading.Event()

camera_1_deque = deque()
camera_2_deque = deque()

events_1_deque = deque()
events_2_deque = deque()

# canvas = Canvas(
#         sensor_width=1280,
#         sensor_height=720,
#         device_primary_events=events_1_deque,
#         device_secondary_events=events_2_deque,
#     )


print("starting")
usb_drive_path = '/Volumes/T7/Calibration_data/'
camera_1_filename = "/Volumes/T7/Calibration_data/primary_ball/2023-10-19T02-54-04.355145Z_00050870_primary.es"
camera_2_filename = "/Volumes/T7/Calibration_data/secondary_ball/2023-10-19T02-54-04.355145Z_00050423_secondary.es"

print(camera_1_filename)
print(camera_2_filename)

event_stream1 = EventStreamReaderOffline(camera_1_filename)
event_stream2 = EventStreamReaderOffline(camera_2_filename)

driver1 = DetectionDriver(np.array((int(event_stream1.get_width()/2),
                                            int(event_stream1.get_height()/2)
                                            )))

driver2 = DetectionDriver(np.array((int(event_stream2.get_width()/2),
                                            int(event_stream2.get_height()/2)
                                            )))

user_input_monitor_thread = threading.Thread(target=user_input_thread)
camera1_thread = threading.Thread(target=thread_camera1, args=(driver1, event_stream1, camera_1_deque, events_1_deque))
camera2_thread = threading.Thread(target=thread_camera2, args=(driver2, event_stream2, camera_2_deque, events_2_deque))
# postion_estimation_thread = threading.Thread(target=triangulate_thread, args=(camera_1_deque, camera_2_deque))

print("Starting all threads")
# user_input_monitor_thread.start()
# camera1_thread.start()
# camera2_thread.start()
# postion_estimation_thread.start()

# vispy.app.run()


# user_input_monitor_thread.join()
# camera1_thread.join()
# camera2_thread.join()
# postion_estimation_thread.join()

def get_pos(chunk, driver):
    events = np.column_stack((chunk['x'], chunk['y']))

    clusters = clustering_dbscan(events)
    position = driver.detect_ball(clusters)


    visualise_single( np.column_stack((chunk['x'], chunk['y'], chunk['on'])), 720, 1280, position, clusters)
 
    return position

def non_thread(event_stream1, event_stream2, driver1, driver2):
    while True:
        chunk1 = event_stream1.get_chunk()
        chunk2 = event_stream2.get_chunk()
        if chunk1 is None or chunk2 is None:
            print("Camera stream1 terminated")
            break

        if len(chunk1) == 0 or len(chunk2) == 0:
            print("No events in chunk")
            continue
        else:
            print(len(chunk1),len(chunk2))
        
        pos1 = get_pos(chunk1, driver1)
        pos2 = get_pos(chunk2, driver2)

        if (pos1 is None or pos2 is None):
            print(f"Ball not found {pos1} {pos2}")
            continue

        estimation = triangulation(pos1, pos2)
        print("estimation: ", estimation)

non_thread(event_stream1, event_stream2, driver1, driver2)