# This will be the script responsible for randomly sampling the regions for 
# our training set and pulling in data to the appropriate folders:
#
# data/data_point_0
# data/...
# data/data_point_n

# Currently set up for a single image per data type we are training on,
# should likely be modified to do this for all images in a directory, etc

import os
import numpy as np
import tifffile

OUTPUT_DIR = '../data/training_data'  # Output directory
WINDOW_SIZE = 100  # Window size for tiles (100 x 100)

def split_image_into_tiles(image_path, image_names, window_size, output_dir):
    # Load the grayscale image
    image = tifffile.imread(image_path)
    
    # Get the image dimensions
    image_height, image_width = image.shape
    
    # Calculate the number of tiles (with overlap)
    step = window_size // 2  # 50% overlap
    tiles = []
    
    # Iterate over the image and extract overlapping tiles
    for y in range(0, image_height - window_size + 1, step):
        for x in range(0, image_width - window_size + 1, step):
            tile = image[y:y + window_size, x:x + window_size]
            tiles.append((x, y, tile))
    
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Save each tile into a new subdirectory
    for i, (x, y, tile) in enumerate(tiles):
        # Generate the subdirectory path
        subdir = os.path.join(output_dir, f"data_point_{i}")
        os.makedirs(subdir, exist_ok=True)
        
        # Save the tile image in the subdirectory
        tile_filename = os.path.join(subdir, f"{image_names}_{x}_{y}.tif")
        tifffile.imsave(tile_filename, tile)
        print(f"Saved tile {i} at {tile_filename}")

if __name__ == "__main__":
    # Set the parameters
    temp_path = '../source_data/temperature.tif'  # Input image file
    temp_names = "temperature"

    # tile the temperature images
    split_image_into_tiles(temp_path, temp_names, WINDOW_SIZE, OUTPUT_DIR)

    # Set the parameters
    hum_path = '../source_data/humidity.tif'  # Input image file
    hum_names = "humidity"

    # tile the humidity images
    split_image_into_tiles(hum_path, hum_names, WINDOW_SIZE, OUTPUT_DIR)
