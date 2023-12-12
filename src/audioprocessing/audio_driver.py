from time import sleep
import numpy as np
from config import POSITIONS_BACK_LOW,POSITIONS_BACK_HIGH,POSITIONS_FRONT_LOW, POSITIONS_FRONT_HIGH
from spatial_audio_processing import spatial_output, get_audio_array

import sounddevice as sd

CHANNELS_OUT = 8
SAMPLE_WIDTH = 2
SAMPLE_RATE = 44100


speaker_positions = np.concatenate((POSITIONS_BACK_LOW,POSITIONS_BACK_HIGH,POSITIONS_FRONT_LOW,POSITIONS_FRONT_HIGH), axis=0)

device_id = None
streams = []
device_name = "Dante Virtual Soundcard (x64)"
#Retrieve the device id 
# NOTE: need to insure that the id order matches position order
devices = sd.query_devices()
for i in range(len(sd.query_devices())):

    if devices[i]["name"] == device_name:
        print(devices[i]["index"], devices[i]["name"])
        
        device_id = i

if device_id is None:
    raise Exception("Dante device not found.")

#Play audio to ensure all speakers connected
try:
    # Play the audio data on the loudspeakers
    mono_audio = get_audio_array()
    audio_data = [mono_audio * 0 for _ in range(len(speaker_positions))]
    audio_data[0] = mono_audio
    audio_data = np.column_stack(audio_data)

    with sd.OutputStream(device=device_id,channels=CHANNELS_OUT, samplerate=44100) as stream:
        stream.start()
        stream.write(audio_data)
        stream.stop()
        sleep(1)
except Exception as e:
    print(f"Error while playing audio: {str(e)}")
    exit()


if __name__ == "__main__":
    def test_from_input():

        while True:
            line = input("Input x y z: ")
            if line == "":
                print("Exiting")
                break
            
            ball_position = np.array([float(x) for x in line.split()])
            
            #Should be an array of audio signals. 
            audio_data = spatial_output(ball_position, speaker_positions,2)

            try:
                # Play the audio data on the loudspeakers

                with sd.OutputStream(device=device_id,channels=CHANNELS_OUT, samplerate=44100) as stream:
                    stream.start()
                    stream.write(audio_data)
                    stream.stop()
            except Exception as e:
                print(f"Error while playing audio: {str(e)}")
                break


    def audio_test_from_file(filename):
        try:
            with open(filename, 'r') as f:
                while True:
                    line = f.readline()
                    if line == "":
                        break
                    if line.strip() == "":
                        print("Break")
                        sleep(2)
                        continue
                    ball_position = np.array([float(x) for x in line.split()])

       
                    audio_data = spatial_output(ball_position, speaker_positions,2)

                    try:
                        # Play the audio data on the loudspeakers
                        with sd.OutputStream(device=device_id,channels=CHANNELS_OUT, samplerate=44100) as stream:
                            stream.start()
                            stream.write(audio_data)
                            stream.stop()
                    except Exception as e:
                        print(f"Error while playing audio: {str(e)}")
                        break
        except FileNotFoundError:
            print("Invalid file")
        
    audio_test_from_file("positions.txt")
