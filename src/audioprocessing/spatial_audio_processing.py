import numpy as np
from config import X_SEP, Y_SEP, Z_SEP


def closest_pair(ball_position, speaker_positions):
		
		distances = np.linalg.norm(speaker_positions - ball_position, axis=1)
		closest_indices = np.argsort(distances)[:2]
		closest_indices.sort()

		return closest_indices

def get_active_speakers(ball_position: np.ndarray, speaker_positions: np.ndarray, row_size: int) -> np.ndarray:

	active_speakers = []

	#NOTE Change bassed on how many rows
	for i in range(4):
		indices = closest_pair(ball_position, speaker_positions[(i)*row_size: (i+1)*row_size])

		offset = i * row_size
		active_speakers.append(indices[0] + offset)
		active_speakers.append(indices[1] + offset)

	#Ordered as consecutive pairs in the same level and side
	#(a1,b1), (c1,d1), (a2,b2), (c2,d2)
	return active_speakers

def get_audio_array():
	audio = []
	with open("shortzz_48000.txt") as f:
		for line in f:
			audio.append(np.float32(line))
	return np.array(audio)


def calculate_weights(ball_position: np.ndarray, speaker_positions: np.ndarray, active_speakers: np.ndarray ):
	dist = []
	for i in active_speakers:
		dist.append(np.absolute(speaker_positions[i] - ball_position))
	print(dist)
	a1, b1, a2, b2, c1, d1, c2, d2 = dist

	a1_w = np.array((c1[0]/X_SEP,  b1[1]/Y_SEP, a2[2]/Z_SEP))
	b1_w = np.array([1,1,1]) - a1_w


	a2_w = np.array((c2[0]/X_SEP,  b2[1]/Y_SEP, a1[2]/Z_SEP))
	b2_w = np.array([1,1,1]) - a2_w

	c1_w = np.array((a1[0]/X_SEP,  d1[1]/Y_SEP, c2[2]/Z_SEP))
	d1_w = np.array([1,1,1]) - c1_w


	c2_w = np.array((a2[0]/X_SEP,  d2[1]/Y_SEP, c1[2]/Z_SEP))
	d2_w = np.array([1,1,1]) - c2_w

	weights = [a1_w, b1_w, a2_w, b2_w, c1_w, d1_w, c2_w, d2_w]

	return [np.prod(w) for w in weights]



def spatial_output(ball_position: np.ndarray, speaker_positions: np.ndarray, row_size: int) -> np.ndarray:
	active_speakers = get_active_speakers(ball_position, speaker_positions, row_size)

	signal_out = [0] * len(speaker_positions)
	
	# Normalize each value to represent a value 0 to 1 based
	weight_array = calculate_weights(ball_position, speaker_positions, active_speakers)
	print("ball: ",ball_position, "weights: ", weight_array)

	audio_signal = get_audio_array()

	for i in range(len(active_speakers)):
		signal_out[active_speakers[i]] = audio_signal * weight_array[i]

	multi_audio = np.column_stack(signal_out)
	return multi_audio










if __name__ == "__main__":
	POSITIONS_BACK_LOW = [(0,0,0.9),(0,01.57,0.9)]
	POSITIONS_BACK_HIGH = [(0,0,1.5),(0,01.57,1.5)]
	POSITIONS_FRONT_LOW = [(0.82,0,0.9),(0.82,1.57,0.9)]
	POSITIONS_FRONT_HIGH = [(0.82,0,1.5),(0.82,1.57,1.5)]


	speaker_positions = np.concatenate((POSITIONS_BACK_LOW,POSITIONS_BACK_HIGH,POSITIONS_FRONT_LOW, POSITIONS_FRONT_HIGH), axis=0)

	result = calculate_weights(np.array((0.4,0,0.9)), speaker_positions, np.array([0,1,2,3,4,5,6,7]))
	print(result)


