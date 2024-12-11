import geopandas as gpd
import rasterio
from rasterio.features import geometry_mask
from shapely.geometry import box
import numpy as np
import os

def rasterize_shapefile(gdf, existing_tif_path, output_tif_path):
    # Ensure the output directory exists
    output_dir = os.path.dirname(output_tif_path)
    os.makedirs(output_dir, exist_ok=True)
    
    # Open the existing tif to get its metadata
    with rasterio.open(existing_tif_path) as src:
        # Get metadata from the existing raster
        transform = src.transform
        width = src.width
        height = src.height
        crs = src.crs
        
        # Get the bounds from the existing raster
        lon_min, lat_min, lon_max, lat_max = src.bounds
        
        # Get the resolution of the existing raster
        resolution_lon = (lon_max - lon_min) / width
        resolution_lat = (lat_max - lat_min) / height
    
    # Reproject the shapefile to match the CRS of the existing raster
    gdf = gdf.to_crs(crs)
    
    # Create the bounding box for the raster (this should match the bounds of the existing raster)
    bbox = box(lon_min, lat_min, lon_max, lat_max)
    
    # Create the mask for the raster
    mask = geometry_mask(gdf.geometry, transform=transform, invert=True, out_shape=(height, width))
    
    # Convert the mask to uint8 (0 for no intersection, 1 for intersection)
    raster_data = np.where(mask, 1, 0)
    
    # Write the raster data to the file
    with rasterio.open(output_tif_path, 'w', driver='GTiff', count=1, dtype='uint8',
                       crs=crs, width=width, height=height, transform=transform) as dst:
        dst.write(raster_data, 1)
    
    print(f"Rasterized shapefile saved to {output_tif_path}")

# Example Usage
shapefile_path = "../data/shapefiles/mtbs_perimeter_data.zip"
# Load the shapefile using geopandas
gdf = gpd.read_file(shapefile_path)
print("Loaded shapefile")

# Path to an existing TIFF file
existing_tif_path = "../data/source_data/land_temp.TIF"

# Output path for the rasterized shapefile
output_tif_path = "../data/source_data/fire_occured.tif"

# Rasterize the shapefile to match the existing TIFF
rasterize_shapefile(gdf, existing_tif_path, output_tif_path)