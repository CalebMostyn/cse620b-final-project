import rasterio
from rasterio.mask import mask
from shapely.geometry import box
import fiona
from fiona.crs import from_epsg

def crop_image(tif_file, output_file, min_lon, min_lat, max_lon, max_lat):
    # Open the GeoTIFF file
    with rasterio.open(tif_file) as src:
        # Check CRS of the file
        src_crs = src.crs
        print(f"CRS of the GeoTIFF: {src_crs}")

        # Create a bounding box in lon/lat
        bbox = box(min_lon, min_lat, max_lon, max_lat)

        # Transform bounding box to the source CRS if it's different
        if src_crs.is_geographic:  # CRS is already lon/lat
            bbox_in_crs = bbox
        else:
            from pyproj import Transformer
            transformer = Transformer.from_crs("EPSG:4326", src_crs)  # EPSG:4326 is WGS84
            x_min, y_min = transformer.transform(min_lat, min_lon)
            x_max, y_max = transformer.transform(max_lat, max_lon)
            bbox_in_crs = box(x_min, y_min, x_max, y_max)

        # Mask the raster with the bounding box
        geojson_geom = [bbox_in_crs.__geo_interface__]
        cropped_image, cropped_transform = mask(src, geojson_geom, crop=True)

        # Update metadata for the cropped image
        out_meta = src.meta.copy()
        out_meta.update({
            "driver": "GTiff",
            "height": cropped_image.shape[1],
            "width": cropped_image.shape[2],
            "transform": cropped_transform
        })

        # Save the cropped GeoTIFF
        with rasterio.open(output_file, "w", **out_meta) as dest:
            dest.write(cropped_image)

# Coordinates (WGS84 / EPSG:4326)  
top_left = (-103.6670, 33.5393) 
top_right = (-102.6837, 33.5393)
bottom_left = (-103.6670, 32.7203)
bottom_right = (-102.6837, 32.7203)

# Create a polygon for the region of interest (ROI)
# roi_polygon = Polygon([top_left, top_right, bottom_right, bottom_left, top_left])

ndvi_path = '../data/source_data/ndvi.TIF'  
ndmi_path = '../data/source_data/ndmi.TIF'  
bai_path = '../data/source_data/bai.TIF'  
land_temp_path = '../data/source_data/land_temp.TIF'  

min_lon, max_lat = top_left
max_lon, min_lat = bottom_right


crop_image(ndvi_path, ndvi_path,min_lon=min_lon, min_lat=min_lat, max_lon=max_lon, max_lat=max_lat)
crop_image(ndmi_path, ndmi_path,min_lon=min_lon, min_lat=min_lat, max_lon=max_lon, max_lat=max_lat)
crop_image(bai_path, bai_path,min_lon=min_lon, min_lat=min_lat, max_lon=max_lon, max_lat=max_lat)
crop_image(land_temp_path, land_temp_path,min_lon=min_lon, min_lat=min_lat, max_lon=max_lon, max_lat=max_lat)