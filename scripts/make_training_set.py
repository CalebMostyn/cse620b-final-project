import os
import numpy as np
import rasterio
from rasterio.windows import Window
import matplotlib.pyplot as plt

OUTPUT_DIR = '../data/training_data'  # Output directory
WINDOW_SIZE = 100  # Window size for tiles (100 x 100)

def split_image_into_tiles(image_path, image_name, window_size, output_dir):
    # Open the image using rasterio
    with rasterio.open(image_path) as src:
        # Get the image dimensions
        image_width = src.width
        image_height = src.height

        # Calculate the number of tiles (with overlap)
        step = window_size // 2  # 50% overlap

        # Ensure the output directory exists
        os.makedirs(output_dir, exist_ok=True)

        # Extract tiles
        tile_index = 0
        for y in range(0, image_height - window_size + 1, step):
            for x in range(0, image_width - window_size + 1, step):
                # Define the window for this tile
                window = Window(x, y, window_size, window_size)
                
                # Read the tile data
                tile = src.read(1, window=window)  # Reading band 1

                # Generate the subdirectory path
                subdir = os.path.join(output_dir, f"data_point_{tile_index}")
                os.makedirs(subdir, exist_ok=True)

                # Save the tile image in the subdirectory
                tile_filename = os.path.join(subdir, f"{image_name}_{x}_{y}.tif")
                with rasterio.open(
                    tile_filename,
                    'w',
                    driver='GTiff',
                    height=window_size,
                    width=window_size,
                    count=1,  # Single band
                    dtype=tile.dtype,
                    crs=src.crs,  # Preserve the coordinate reference system
                    transform=rasterio.windows.transform(window, src.transform)
                ) as dst:
                    dst.write(tile, 1)

                print(f"Saved tile {tile_index} at {tile_filename}")
                tile_index += 1

if __name__ == "__main__":
    # Set the parameters
    temp_path = '../data/source_data/temperature_new.tif'  # Input image file
    temp_name = "temperature"

    # Tile the temperature images
    split_image_into_tiles(temp_path, temp_name, WINDOW_SIZE, OUTPUT_DIR)

    # Set the parameters
    hum_path = '../data/source_data/humidity_new.tif'  # Input image file
    hum_name = "humidity"

    # Tile the humidity images
    split_image_into_tiles(hum_path, hum_name, WINDOW_SIZE, OUTPUT_DIR)
