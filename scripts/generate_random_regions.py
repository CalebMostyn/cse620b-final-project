# This script is intended to create a random set of regions to pull source data from.
# Training data will be a smaller subset of images pulled out of that region.

# If we are windowing with 50% overlap, that means a region of that is X * Window Size by Y * Window Size
# will produce 2 * X * Y data points for training. Ideally we want at least a hundred observations per type of data we train on,
# so the sum of all the regions 2 * X * Y values should be 100 * data types.

import random
import math
from datetime import datetime, timedelta

# Constants
WINDOW_SIZE = 3  # 3 km (30m spatial resolution, 100x100 pixel images)
RESULT_PATH = "../data/source_data.txt"  # File path to save the results
NUM_OBSERVATIONS = 600 # Should ideally be at least 100 times the types of data we are training on
MAX_REGION_WIDTH = 10 # Bounding box for a region will be no more than this times the window size (width or height)

# Approximate bounding box for the United States (latitude, longitude ranges)
USA_BOUNDS = {
    "min_lat": 24.396308,  # Southernmost point
    "max_lat": 49.384358,  # Northernmost point
    "min_lon": -125.0,     # Westernmost point
    "max_lon": -66.93457   # Easternmost point
}

def generate_random_coordinate():
    """Generates a random latitude and longitude within the USA bounds."""
    lat = random.uniform(USA_BOUNDS["min_lat"], USA_BOUNDS["max_lat"])
    lon = random.uniform(USA_BOUNDS["min_lon"], USA_BOUNDS["max_lon"])
    return lat, lon

def create_rectangle(window_size):
    """Creates a rectangle with side lengths as multiples of `window_size`."""
    lat, lon = generate_random_coordinate()
    width = random.randint(1, MAX_REGION_WIDTH) * window_size
    height = random.randint(1, MAX_REGION_WIDTH) * window_size
    
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

    while total_num_tiles < NUM_OBSERVATIONS:
        rectangle, width, height = create_rectangle(WINDOW_SIZE)
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