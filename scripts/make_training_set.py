import os
import numpy as np
import rasterio
import argparse
from rasterio.windows import Window
import matplotlib.pyplot as plt

def split_image_into_tiles(image_path, image_name, window_size, output_dir, overlap):
    """
    Splits an image into tiles with a specified overlap percentage.

    Args:
        image_path (str): Path to the input image.
        image_name (str): Name prefix for the output tiles.
        window_size (int): Size of each square tile (in pixels).
        output_dir (str): Directory where the tiles will be saved.
        overlap (float): Overlap percentage between tiles (range [0, 1]).
    """
    # Open the image using rasterio
    with rasterio.open(image_path) as src:
        # Get the image dimensions
        image_width = src.width
        image_height = src.height

        # Calculate the step size based on the overlap
        step = int(window_size * (1 - overlap))

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

def process_directory(source_dir, dest_dir, window_size, overlap):
    """
    Process all images in a directory, splitting each into tiles.

    Args:
        source_dir (str): Directory containing input images.
        dest_dir (str): Directory where the tiles will be saved.
        window_size (int): Size of each square tile (in pixels).
        overlap (float): Overlap percentage between tiles (range [0, 1]).
    """
    # Ensure the output directory exists
    os.makedirs(dest_dir, exist_ok=True)

    # Process each file in the source directory
    for file_name in os.listdir(source_dir):
        if file_name.endswith(('.tif', '.tiff', '.TIF')):  # Process only .tif or .tiff files
            image_path = os.path.join(source_dir, file_name)
            image_name, _ = os.path.splitext(file_name)
            
            print(f"Processing image: {image_path}")
            split_image_into_tiles(image_path, image_name, window_size, dest_dir, overlap)

def main():
    parser = argparse.ArgumentParser(description="Split large images into smaller, overlapping tiles.")
    parser.add_argument('--source_dir', required=True, help="Directory containing source image files.")
    parser.add_argument('--dest_dir', default='../data/training_data', help="Folder for Tiled Images to be Saved to")
    parser.add_argument('--window_size', type=int, default=100, help="Pixels in tiled images, [window_size] by [window_size]")
    parser.add_argument('--overlap', type=float, default=0.5, help="Percentage of tile overlap, in the range [0,1]")
    args = parser.parse_args()

    # Process the directory of images
    process_directory(args.source_dir, args.dest_dir, args.window_size, args.overlap)

if __name__ == "__main__":
    main()