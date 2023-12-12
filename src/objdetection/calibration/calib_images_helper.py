import numpy as np
import event_stream
import matplotlib.pylab as plt
import matplotlib
import os
import colourtime
from typing import List
import PIL.Image

def create_calib_images(folder_path: str) -> List[PIL.Image.Image]:
	file_paths = []
	for file in os.listdir(folder_path ):
		file_path = os.path.join(folder_path + file)
		if file_path.endswith(".es"):
			file_paths.append(file_path)


	images_ls = []
	for f in file_paths:
		decoder = event_stream.Decoder(f)

		width = decoder.width
		height = decoder.height
		background_colour = (1.0,1.0,1.0,1.0)


		img_cyclic = colourtime.convert(0, 1e6, width, height, decoder, matplotlib.colormaps['binary'],
								colourtime.generate_cyclic_time_mapping(1e6/6, 0), 0.2, background_colour)
		
		img_linear = colourtime.convert(1e6,2e6, width, height, decoder, matplotlib.colormaps['bone'], 
									colourtime.generate_cyclic_time_mapping(1e6/6,1e6), 0.1, background_colour)
		images_ls.append(img_cyclic)
		images_ls.append(img_linear)
	print(f"{len(images_ls)} images created")
	return images_ls