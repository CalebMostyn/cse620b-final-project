# This script is intended to create a random set of regions to pull source data from.
# Training data will be a smaller subset of images pulled out of that region.

# If we are windowing with 50% overlap, that means a region of that is X * Window Size by Y * Window Size
# will produce 2 * X * Y data points for training. Ideally we want at least a hundred observations per type of data we train on,
# so the sum of all the regions 2 * X * Y values should be 100 * data types.

import random
import math
from datetime import datetime, timedelta
from shapely.geometry import Point, Polygon, box
import geopandas as gpd


# Constants
WINDOW_SIZE = 3  # 3 km (30m spatial resolution, 100x100 pixel images)
RESULT_PATH = "../data/source_data/source_data.txt"  # File path to save the results
US_SHAPEFILE_PATH = "../data/shapefiles/cb_2018_us_nation_5m.zip" # Shapefile representing US borders
NUM_OBSERVATIONS = 200 # Should ideally be at least 100 times the types of data we are training on
MIN_REGION_WIDTH = 10 # Bounding box for a region will be no less than this times the window size (width or height)
MAX_REGION_WIDTH = 15 # Bounding box for a region will be no more than this times the window size (width or height)
MERRA_BOUNDS = [(-123.925, 52.925), (-89.025, 25.065)] # Bounds of the 1km resolution MERRA data

# Load the U.S. shapefile
def load_us_boundary():
    """Loads the U.S. boundary polygon from a shapefile."""
    gdf = gpd.read_file(US_SHAPEFILE_PATH)
    us_polygon = gdf.unary_union  # Combine all geometries into one
    return clip_polygon_to_rectangle(us_polygon, MERRA_BOUNDS[0], MERRA_BOUNDS[1])

def clip_polygon_to_rectangle(polygon, top_left, bottom_right):
    """
    Clips the given polygon to a rectangle defined by top-left and bottom-right coordinates.
    
    Args:
        polygon (shapely.geometry.Polygon): The polygon to be clipped.
        top_left (tuple): Coordinates (lon, lat) of the top-left corner of the rectangle.
        bottom_right (tuple): Coordinates (lon, lat) of the bottom-right corner of the rectangle.
        
    Returns:
        shapely.geometry.Polygon: The clipped polygon.
    """
    # Create a bounding box polygon
    minx, maxy = top_left
    maxx, miny = bottom_right
    bounding_box = box(minx, miny, maxx, maxy)
    
    # Clip the polygon
    clipped_polygon = polygon.intersection(bounding_box)
    return clipped_polygon

def generate_random_coordinate_within_polygon(polygon):
    """Generates a random coordinate within a given polygon."""
    minx, miny, maxx, maxy = polygon.bounds
    while True:
        lat = random.uniform(miny, maxy)
        lon = random.uniform(minx, maxx)
        point = Point(lon, lat)
        if polygon.contains(point):
            return lat, lon

def create_rectangle(window_size,polygon):
    """Creates a rectangle with side lengths as multiples of `window_size`."""
    lat, lon = generate_random_coordinate_within_polygon(polygon)
    width = random.randint(MIN_REGION_WIDTH, MAX_REGION_WIDTH) * window_size
    height = random.randint(MIN_REGION_WIDTH, MAX_REGION_WIDTH) * window_size
    
    # Convert width and height into approximate degree offsets
    lat_offset = height / 111  # Approximation: 1 degree latitude ~ 111 km
    lon_offset = width / (111 * abs(math.cos(math.radians(lat))))  # Adjust for longitude shrinkage
    
    # Define the rectangle corners
    top_left = (lat, lon)
    top_right = (lat, lon + lon_offset)
    bottom_left = (lat - lat_offset, lon)
    bottom_right = (lat - lat_offset, lon + lon_offset)
    
    return [top_left, top_right, bottom_left, bottom_right], width, height

def convert_days_to_date(days):
    """Converts the number of days since Jan 1, 2023 to a formatted date string."""
    start_date = datetime(2023, 1, 1)  # January 1st, 2023
    date = start_date + timedelta(days=days)  # Add the days to the start date
    return date.strftime("%Y-%m-%d")  # Format the date as 'YYYY-MM-DD'

def save_rectangles(rectangles, file_path):
    """Saves a list of rectangles to a file with properly aligned columns."""
    with open(file_path, "w") as f:
        # Write the header line
        f.write(f"{'(Top Left)':<25}{'(Top Right)':<25}{'(Bottom Left)':<25}{'(Bottom Right)':<25}{'(Date)':<25}\n")
        
        # Write each rectangle
        for rect in rectangles:
            rect_str = "".join([f"{f'({lat:.6f}, {lon:.6f})':<25}" for lat, lon in rect])

            random_date = random.randint(0, 364)
            rect_str += f"{convert_days_to_date(random_date):<10}" 
            f.write(rect_str + "\n")



def main():
    total_num_tiles = 0
    rectangles = []
    us_polygon = load_us_boundary()

    while total_num_tiles < NUM_OBSERVATIONS:
        rectangle, width, height = create_rectangle(WINDOW_SIZE, us_polygon)
        print(f"Width - {width} : Height - {height}")
        num_tiles = (math.floor((width - WINDOW_SIZE) / (WINDOW_SIZE / 2)) + 1) * \
                    (math.floor((height - WINDOW_SIZE) / (WINDOW_SIZE / 2)) + 1)
        total_num_tiles += num_tiles
        rectangles.append(rectangle)

    save_rectangles(rectangles, RESULT_PATH)
    print(f"Saved {len(rectangles)} rectangles to {RESULT_PATH}")
    print(f"Total Number of Observations: {total_num_tiles}")

if __name__ == "__main__":
    main()
