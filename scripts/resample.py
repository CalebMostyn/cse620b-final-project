import rasterio
from rasterio.enums import Resampling
import numpy as np

def resample_raster(input_file, output_file, target_resolution):
    """
    Resamples a raster file to a specified spatial resolution.

    Parameters:
    - input_file (str): Path to the input raster file.
    - output_file (str): Path to save the resampled raster file.
    - target_resolution (float): Target spatial resolution in the same units as the input raster.
    """
    with rasterio.open(input_file) as src:
        # Calculate the scaling factor
        scale_x = src.res[0] / target_resolution
        scale_y = src.res[1] / target_resolution

        # Calculate new dimensions
        new_width = int(src.width * scale_x)
        new_height = int(src.height * scale_y)

        # Read the data and resample
        data = src.read(
            out_shape=(src.count, new_height, new_width),
            resampling=Resampling.bilinear
        )

        # Update transform to reflect new resolution
        transform = src.transform * src.transform.scale(
            (src.width / new_width),
            (src.height / new_height)
        )

        # Save the resampled raster
        profile = src.profile
        profile.update({
            'transform': transform,
            'width': new_width,
            'height': new_height
        })

        with rasterio.open(output_file, 'w', **profile) as dst:
            dst.write(data)

# Example usage
input_file = "../data/source_data/og_humidity.tiff"  # Path to your input file
output_file = "../data/source_data/humidity.tif"  # Path to save the resampled file
target_resolution = 30 / 111000  # Convert 30m to degrees (approximately)
resample_raster(input_file, output_file, target_resolution)