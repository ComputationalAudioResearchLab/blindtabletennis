# blindtabletennis
Event camera and loud speaker system for assisted blind table tennis. This repository contains the code for the e2e system of blind table tennis

# Dependencies

## Python packages
To get started, install the folowing python packages through pip

- neuromorphic_drivers
- event_stream
- vispy
- numpy 
- sounddevice
- colourtime
- Pillow
- matplotlib
- cv2
- sklearn

## Hardware 

Prophesee event camera (DVS gen 4)
Loud speakers with ethernet connection (Configure channels with Dante)


# Documentation 


## Calibration

Before running the main program, calibration needs to be completed.

### Camera Calibration

Use `record_calibrate` to take short 4 second recordings from the cameras. The `dynamic_checkerboard.mp4` video in the `calibrate` folder can be used. A minimum 10 recordings is ideal.

Adjust the `dirname` in `calibrate_camera` to the folder with the recordings. Run `calibrate_camera`. This will render the event streams and may take a bit of time. If majority of rendered images produce coloured detection lines, the calibration is successful.

Note that translation and rotation of camera 1 is treated as the basis to measure camera 2.

### Speaker calibration

TO DO

Speaker positions need to be found in relation to the cameras. Theorectically this could be done by using the cameras to triangulate. Standard procedure has not been properly developed. 

## Running the program

`offline_main.py` can be used to run the offline version which is used on the recorded event streams. Change the files to the desired recordings before running.

`main.py` can be used to run the live version of the system. Note currently this is untested.

## Code

### objdetection
This package handles the event camera part of the pipeline.

`eventprocessing` contains two versions for offline stream `event_stream_reader` and online stream `event_buffer`

`detectiondriver` contains the class that handles the states of each event stream detection. It stores the previous position of the ball.

`clustering` handles the DBSCAN algorithm and also the weighting of each cluster using `cluster_weight_measure`. It also contains additional methods used for detecting a laser pointed at a speaker for speaker position retrieval. 

`position_estimation` is used for triangulation of two points to get 3D position

### display 

This package contains the code that handles the visualisation of the event streams. Note the `visualise` package in `objdetection` is for convenience during testing and not actually used in the system. 

### audioprocessing

This package handles the audio component of the pipeline. The `audio_driver` communicates with the channels to render the audio signal. `spatial_audio_processing` is used to calculate which speakers are active and what level of amplitude to play at.