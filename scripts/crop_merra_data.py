import rasterio
from rasterio.warp import reproject, Resampling
from rasterio.enums import ColorInterp
from rasterio.transform import from_origin
import numpy as np

def reproject_and_crop(source_tif, dest_tif, output_tif):
    # Open the source and destination TIFF files
    with rasterio.open(source_tif) as src:
        with rasterio.open(dest_tif) as dst:
            # Get the CRS of the destination TIFF
            dest_crs = dst.crs
            
            # Create a transform for the destination TIFF
            dest_transform = dst.transform
            dest_width = dst.width
            dest_height = dst.height
            
            # Reproject the source TIFF to the destination's CRS
            # The shape of the output is the size of the destination TIFF
            src_array = src.read(1)  # Read the source image
            src_crs = src.crs
            src_transform = src.transform
            output_array = np.zeros((dest_height, dest_width), dtype=np.float32)

            # Reprojecting the source image to match the destination's CRS and transform
            reproject(
                src_array,
                output_array,
                src_crs=src_crs,
                src_transform=src_transform,
                dst_crs=dest_crs,
                dst_transform=dest_transform,
                resampling=Resampling.nearest
            )

            # Get the bounding box of the destination image
            dest_bounds = dst.bounds

            # Crop the reprojected source image to match the destination bounds
            row_start, col_start = ~dest_transform * (dest_bounds[0], dest_bounds[3])
            row_end, col_end = ~dest_transform * (dest_bounds[2], dest_bounds[1])

            # Convert to integer indices
            row_start, col_start = int(row_start), int(col_start)
            row_end, col_end = int(row_end), int(col_end)

            # Crop the reprojected image
            cropped_array = output_array[row_start:row_end, col_start:col_end]

            # Save the cropped, reprojected image to a new file
            profile = dst.profile
            profile.update(
                dtype=rasterio.float32,
                count=1,
                compress='lzw',
                crs=dest_crs,
                transform=dest_transform
            )

            with rasterio.open(output_tif, 'w', **profile) as out:
                out.write(cropped_array, 1)

            print(f"Reprojected and cropped image saved to {output_tif}")

# Example usage
source_tif = "../data/source_data/air_temp.tif"
dest_tif = "../data/source_data/ndvi.TIF"
output_tif = "../data/source_data/air_temp.tif"

reproject_and_crop(source_tif, dest_tif, output_tif)