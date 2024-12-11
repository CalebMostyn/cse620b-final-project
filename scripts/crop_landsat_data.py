import rasterio
import matplotlib.pyplot as plt
from shapely.geometry import Polygon
from rasterio.mask import mask
from pyproj import CRS
from shapely.ops import transform
import geopandas as gpd

def crop_image(path, roi_polygon):
    # Open the TIFF file and get the CRS
    with rasterio.open(path) as src:
        # Check the CRS of the raster
        raster_crs = CRS.from_wkt(src.crs.wkt)

        # Reproject the polygon to match the raster CRS (if different)
        if raster_crs != CRS.from_epsg(4326):
            # Use geopandas for CRS transformation
            geo_df = gpd.GeoDataFrame([{'geometry': roi_polygon}], crs="EPSG:4326")
            geo_df = geo_df.to_crs(raster_crs)
            roi_polygon = geo_df.geometry[0]

        # Apply a small buffer to the polygon to ensure full coverage
        roi_polygon = roi_polygon.buffer(0.0001)  # Adjust the buffer size as necessary

        # Mask the raster data with the polygon to extract the region of interest
        geo_json = roi_polygon.__geo_interface__
        out_image, out_transform = mask(src, [geo_json], crop=True, all_touched=True)

        # Squeeze out the unnecessary dimension for the number of bands
        out_image = out_image.squeeze(0)  # Remove the first dimension if it's 1

        # Define metadata for the new TIFF file
        out_meta = src.meta.copy()
        out_meta.update({
            "driver": "GTiff",  # Output file format
            "count": 1,  # Single-band image
            "dtype": out_image.dtype,  # Data type
            "crs": src.crs,  # Coordinate Reference System
            "transform": out_transform,  # Affine transform for the new image
            "width": out_image.shape[1],  # New image width
            "height": out_image.shape[0],  # New image height
        })

        # Save the masked image as a new TIFF file
        with rasterio.open(path, "w", **out_meta) as dest:
            dest.write(out_image, 1)  # Write the first band of the masked image

# Coordinates (WGS84 / EPSG:4326)  
top_left = (-103.6670, 33.5393) 
top_right = (-102.6837, 33.5393)
bottom_left = (-103.6670, 32.7203)
bottom_right = (-102.6837, 32.7203)

# Create a polygon for the region of interest (ROI)
roi_polygon = Polygon([top_left, top_right, bottom_right, bottom_left, top_left])

ndvi_path = '../data/source_data/ndvi.TIF'  
ndmi_path = '../data/source_data/ndmi.TIF'  
bai_path = '../data/source_data/bai.TIF'  
land_temp_path = '../data/source_data/land_temp.TIF'  


crop_image(ndvi_path, roi_polygon)
crop_image(ndmi_path, roi_polygon)
crop_image(bai_path, roi_polygon)
crop_image(land_temp_path, roi_polygon)