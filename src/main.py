import time

import neuromorphic_drivers as nd
import numpy as np

from collections import deque
import threading

import time
from objdetection.detection_driver import DetectionDriver
from objdetection.clustering import clustering_dbscan
import objdetection.calibration.config as config
import numpy as np
import vispy.app

from objdetection.position_estimation import triangulation
from objdetection.eventprocessing.event_buffer import EventBuffer

from audioprocessing.audio_driver import AudioDriver

from display.display_interface import Canvas


exit_event = threading.Event()

def thread_camera1(driver: DetectionDriver, pos_deque: deque, buffer: EventBuffer):
    print("Camera 1 thread staring")
    while not exit_event.is_set():
        chunk = buffer.get_chunk()

        if chunk is None:
            continue

        events_1_deque.append(chunk)


        # mask = chunk["on"] == 1

        events = np.column_stack((chunk['x'], chunk['y']))
        #np.lib.recfunctions structured to unstructured 

        clusters = clustering_dbscan(events)
        position = driver.detect_ball(clusters)
        pos_deque.append(position)

 

def thread_camera2(driver: DetectionDriver, pos_deque: deque, buffer: EventBuffer):
    print("Camera 2 thread staring")
    while not exit_event.is_set():
        chunk = buffer.get_chunk()

        events_2_deque.append(chunk)
        
        if chunk is None:
            continue

        # mask = chunk["on"] == 1
        events = np.column_stack((chunk['x'], chunk['y']))

        clusters = clustering_dbscan(events)
        position = driver.detect_ball(clusters)
        pos_deque.append(position)


def user_input_thread():
    while True:
        user_input = input("Enter 'exit' to terminate the program: \n")
        if user_input.lower() == 'exit':
            exit_event.set()
            break

def triangulate_thread(camera_1_deque: deque, camera_2_deque: deque, pos_deque: deque):
    print("Starting triangulate Thread")
    while not exit_event.is_set():
        if len(camera_1_deque) > 0 and len(camera_2_deque) > 0:
            pos1 = camera_1_deque.popleft()
            pos2 = camera_2_deque.popleft()
            if (pos1 is None or pos2 is None):
                print("Ball not found", pos1, pos2)
                continue
            estimation = triangulation(pos1, pos2)
            pos_deque.append(estimation)
            # Print the 3D coordinates of the object
            print("3D Coordinates of the Object:")
            print(f"X: {estimation[0]}")
            print(f"Y: {estimation[1]}")
            print(f"Z: {estimation[2]}")

def audio_thread(pos_deque:deque, audio_driver: AudioDriver):
    print("Starting Audio thread")
    while not exit_event.is_set():
        if(len(pos_deque)> 0):
            audio_driver.run(pos_deque.popleft())




#Setting up camera ports
PRIMARY_SERIAL = "00050423"
SECONDARY_SERIAL = "00050870"
secondary_device = nd.open(
    serial=SECONDARY_SERIAL,
    raw=True,
    iterator_timeout=0.1,
    configuration=nd.prophesee_evk4.Configuration(
        nd.prophesee_evk4.Biases(
            diff_on=120,
            diff_off=120,
        ),
        clock=nd.prophesee_evk4.Clock.EXTERNAL,
    ),
)
time.sleep(1.0)  # wait to make sure that secondary is ready
primary_device = nd.open(
    serial=PRIMARY_SERIAL,
    raw=True,
    iterator_timeout=0.1,
    configuration=nd.prophesee_evk4.Configuration(
        nd.prophesee_evk4.Biases(
            diff_on=120,
            diff_off=120,
        ),
        clock=nd.prophesee_evk4.Clock.INTERNAL_WITH_OUTPUT_ENABLED,
    ),
)
devices = [primary_device, secondary_device]

#Threads set up
result_update_1 = threading.Event()
result_update_2 = threading.Event()

camera_1_deque = deque()
camera_2_deque = deque()

events_1_deque = deque()
events_2_deque = deque()

pos_deque = deque()

driver1 = DetectionDriver(np.array((config.WIDTH/2,config.HEIGHT/2)))

driver2 = DetectionDriver(np.array((config.WIDTH/2,config.HEIGHT/2)))

audio_driver = AudioDriver()

canvas = Canvas(
        sensor_width=int(primary_device.properties().width),
        sensor_height=int(primary_device.properties().height),
        device_primary_events=events_1_deque,
        device_secondary_events=events_2_deque,
    )

camera1_thread = threading.Thread(target=thread_camera1, args=(driver1, camera_1_deque, events_1_deque))
camera2_thread = threading.Thread(target=thread_camera2, args=(driver2, camera_2_deque, events_2_deque))
user_input_monitor_thread = threading.Thread(target=user_input_thread)
postion_estimation_thread = threading.Thread(target=triangulate_thread, args=(camera_1_deque, camera_2_deque, pos_deque))
audio_thread = threading.Thread(target=audio_thread, args=(audio_driver, pos_deque))

print("Starting all threads")

user_input_monitor_thread.start()
camera1_thread.start()
camera2_thread.start()
#Give the cameras time to be set up before attempt triangulation
time.sleep(0.1)
postion_estimation_thread.start()

vispy.app.run()

print("Joining threads")
camera1_thread.join()
camera2_thread.join()
user_input_monitor_thread.join()

    






