import rasterio
import numpy as np

# Constants for Landsat 8
K1 = 774.89  # Calibration constant for Band 10 (K1) for Landsat 8
K2 = 1321.08  # Calibration constant for Band 10 (K2) for Landsat 8
L_min = 0  # Min radiance for Band 10
L_max = 255  # Max radiance for Band 10
EMISSIVITY = 0.98  # Surface emissivity, assumed as 0.98 for land

# Function to calculate TOA Radiance
def calculate_toa_radiance(dn, gain, bias):
    """
    Converts Digital Numbers (DN) to Top-of-Atmosphere (TOA) Radiance
    """
    return (dn * gain) + bias

def calculate_brightness_temperature(radiance, K1, K2):
    """
    Convert TOA Radiance to Brightness Temperature in Kelvin
    Ensure that the radiance is positive before applying the log function.
    """
    # Clamp radiance values to avoid log of zero or negative values
    radiance = np.maximum(radiance, 1e-6)  # Ensure radiance is > 0

    # Apply the brightness temperature formula
    return K2 / np.log((K1 / radiance) + 1)

# Function to calculate LST
def calculate_lst(band10_filename):
    # Open the Band 10 TIRS image
    with rasterio.open(band10_filename) as src:
        # Read the image data (assumes single-band image)
        band10_data = src.read(1)
        
        # Calibration constants for Band 10 (assuming DN to Radiance conversion)
        gain = 0.0003342  # Gain for Band 10
        bias = 0.1  # Bias for Band 10
        
        # Apply radiometric calibration (DN to TOA Radiance)
        radiance = calculate_toa_radiance(band10_data, gain, bias)
        
        # Convert radiance to brightness temperature in Kelvin
        brightness_temp_kelvin = calculate_brightness_temperature(radiance, K1, K2)
        
        # Convert Kelvin to Celsius
        brightness_temp_celsius = brightness_temp_kelvin - 273.15
        
        # Adjust for land emissivity (typically 0.98 for land)
        lst = brightness_temp_celsius / EMISSIVITY
        
        return lst


def save_tif_rasterio(output_path, data, reference_path):
    with rasterio.open(reference_path) as src:
        metadata = src.meta
    metadata.update(dtype=rasterio.float32, count=1)
    with rasterio.open(output_path, 'w', **metadata) as dst:
        dst.write(data, 1)


# Path to your Landsat TIFF file (replace with actual file path)
red_path = '../data/source_data/b4.TIF'
nir_path = '../data/source_data/b5.TIF'
swir_path = '../data/source_data/b6.TIF'
tirs_path = '../data/source_data/b10.TIF'
# Path to save the output
ndvi_path = '../data/source_data/ndvi.TIF'  
ndmi_path = '../data/source_data/ndmi.TIF'  
bai_path = '../data/source_data/bai.TIF'  
land_temp_path = '../data/source_data/land_temp.TIF'  

# Open and read the data from each TIFF file
with rasterio.open(red_path) as red:
    red_data = red.read(1)  # Read the first band (red)

with rasterio.open(nir_path) as nir:
    nir_data = nir.read(1)  # Read the first band (NIR)

with rasterio.open(swir_path) as swir:
    swir_data = swir.read(1)  # Read the first band (SWIR)

with rasterio.open(tirs_path) as tirs:
    tirs_data = tirs.read(1)  # Read the first band (TIRS)

# Avoid division by zero by masking out invalid pixels
denominator_ndvi = nir_data + red_data
denominator_ndmi = nir_data + swir_data

# Mask out where the denominator is 0 or very close to 0
ndvi_data = np.divide(nir_data - red_data, denominator_ndvi, where=(denominator_ndvi != 0))
ndmi_data = np.divide(nir_data - swir_data, denominator_ndmi, where=(denominator_ndmi != 0))

bai_data = 1 / ((0.1 - red_data) ** 2) + ((0.06 - nir_data) ** 2)
land_temp_data = calculate_lst(tirs_path)

# Save the data as .TIF files using rasterio
save_tif_rasterio(ndvi_path, ndvi_data, red_path)
save_tif_rasterio(ndmi_path, ndmi_data, red_path)
save_tif_rasterio(bai_path, bai_data, red_path)
save_tif_rasterio(land_temp_path, land_temp_data, red_path)