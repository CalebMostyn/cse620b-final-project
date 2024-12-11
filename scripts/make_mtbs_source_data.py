import geopandas as gpd
import rasterio
from rasterio.features import geometry_mask
from shapely.geometry import box
import numpy as np
import os

def rasterize_shapefile(gdf, lon_min, lon_max, lat_min, lat_max, resolution_meters, output_tif_path):
    # Ensure the output directory exists
    output_dir = os.path.dirname(output_tif_path)
    os.makedirs(output_dir, exist_ok=True)
    
    # Define the bounding box for the raster
    bbox = box(lon_min, lat_min, lon_max, lat_max)
    
    # Reproject the shapefile to the same CRS as the bounding box (WGS84 is EPSG:4326)
    gdf = gdf.to_crs(epsg=4326)
    
    # Convert resolution from meters to degrees
    avg_latitude = (lat_min + lat_max) / 2  # Average latitude for the bounding box
    meters_per_degree_lat = 111320  # Approximate meters per degree latitude
    meters_per_degree_lon = 111320 * np.cos(np.radians(avg_latitude))  # Adjust for latitude
    
    resolution_lon = resolution_meters / meters_per_degree_lon
    resolution_lat = resolution_meters / meters_per_degree_lat
    
    # Calculate the number of pixels in both directions
    width = int((lon_max - lon_min) / resolution_lon)
    height = int((lat_max - lat_min) / resolution_lat)
    
    # Add check to ensure dimensions are positive
    if width <= 0 or height <= 0:
        raise ValueError(f"Invalid raster dimensions: width = {width}, height = {height}. Ensure the bounding box is correct and resolution is appropriate.")
    
    # Create the transformation (affine matrix)
    transform = rasterio.transform.from_origin(lon_min, lat_max, resolution_lon, resolution_lat)
    
    # Create the raster file and write the data
    with rasterio.open(output_tif_path, 'w', driver='GTiff', count=1, dtype='uint8',
                       crs='EPSG:4326', width=width, height=height, transform=transform) as dst:
        
        # Create a mask where True (1) represents pixels inside the polygons, False (0) otherwise
        mask = geometry_mask(gdf.geometry, transform=transform, invert=True, out_shape=(height, width))
        
        # Convert the mask to uint8 (0 for no intersection, 1 for intersection)
        raster_data = np.where(mask, 1, 0)
        
        # Write the raster data to the file
        dst.write(raster_data, 1)

    print(f"Rasterized shapefile saved to {output_tif_path}")

# Example Usage
shapefile_path = "../data/shapefiles/mtbs_perimeter_data.zip"
# Load the shapefile using geopandas
gdf = gpd.read_file(shapefile_path)
print("loaded shapefile")

top_left = (-103.6670, 33.5393) 
top_right = (-102.6837, 33.5393)
bottom_left = (-103.6670, 32.7203)
bottom_right = (-102.6837, 32.7203)

resolution = 30  # 30 meters
lon_min, lat_max = top_left
lon_max, lat_min = bottom_right
output_tif_path = f"../data/source_data/fire_occured.tif"
rasterize_shapefile(gdf, lon_min, lon_max, lat_min, lat_max, resolution, output_tif_path)



