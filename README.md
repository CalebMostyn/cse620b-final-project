# cse620b-final-project
Random Forest Model for Identifying Wildfire Risk from GIS and Remote Sensing Data 

Ryan Holthouse, Caleb Mostyn, Julia Loncala, Seth Peppo

## Requirements
```
conda install --file requirements.txt
```

## Project Structure
```
project/
├── data/
│   ├── source_data/                    # Larger Source Files
│   │   └── source_data.txt             # Definition of Data Source Regions (long, lat)
│   ├── shapefiles/                     # Shapefiles
│   │   ├── cb_2018_us_nation_5m.zip    # United States Borders
│   │   └── mtbs_perimeter_data.zip     # Burned Area Regions
│   └── training_data/                  # N Observations Split into Individual Folders
│       ├── data_point_0/               # Data Files for Observation 0
│       ├── .../                        # ...
│       └── data_point_n/               # Data Files for Observation N
├── notebooks/                          # Jupyter Notebooks
│   └── merra_work.ipynb                # Notebook for Isolating Source Region from US MERRA Data
├── scripts/                            # Python Scripts
│   ├── generate_random_regions.py      # Script to Randomly Generate Regions for Data
│   ├── make_landsat_source_data.py     # Script to Calculate NDVI, NDMI, BAI, and Surface Temp
│   ├── make_mtbs_source_data.py        # Script to Create a Rasterized Version of the MTBS Polygons
│   ├── make_training_set.py            # Script to Break Data Regions into N Observations
│   ├── crop_landsat_data.py            # Script to Cut Landsat Source Images to Specified Region
│   ├── crop_merra_data.py              # Script to Reproject and Crop the Resampled MERRA data
│   ├── resample.py                     # Script to Resample Low Resolution Data
│   └── model.py                        # Trains a Random Forest on Training Data Set
├── saved_model/                        # Model Files
├── results/                            # Result Images (Confusion Matrix, Sample Output, etc)
├── LICENSE                             # MIT License
├── requirements.txt                    # Project Requirements
└── README.md                           # Project Description
```

## Data
Training data is sourced from:
- [LANDSAT 8](https://landsat.gsfc.nasa.gov/satellites/landsat-8/)
- [MERRA-2](https://gmao.gsfc.nasa.gov/reanalysis/merra-2/)
- [MTBS](https://www.mtbs.gov/)

The Spatial Resolution of each dataset is as follows:
- LANDSAT 8: 30m (Visible Spectrum, NIR, SWIR) and 100m (Thermal Data)
- MERRA 2: 1.1km
- MODIS: 250m (Land/Cloud/Aerosols Boundaries), 500m (Land/Cloud/Aerosols Properties), 1000m (All Other Bands)

To preserve the detail of the LANDSAT data, it would be ideal to use a resolution of 30m or 100m. For data with higher resolution than the chosen resolution, it will require downsampling, and for data with lower resolution (more of an issue here) it will require upsampling.

To begin with, observations will be windowed at 100 pixels by 100 pixels at 30m resolution. To improve performance of the model at the cost of computation complexity and number of observations, this size may be increased.

Temporally, data points will be limited to the year 2023. We feel recent data is the most relevant to the purpose of the model, and covering the span of a year, we may be able to cover variations in seasons that could impact wildfire risk.

The complete data set will be created by first generating some large, bounding boxes of regions of the United States. If it is benefecial to the model, we may generate this regions at random, but it may also be beneficial to select representative regions of different climate, vegatation makeup, etc. A random date will be generated for the region, and then that region at that time will be downloaded from the various data sources manually. For code related to this see `generate_random_regions.py`.

Then, each region will be broken into individual observations by cutting the data into overlapping windows of our defined size (3000m by 3000m). Overlapping the windows of the observations should benefit the model by allowing it to pick up on contextual data that may otherwise be cut off by the bounds of the window, as well as generally increasing the data points used to train the model without increasing the amount of source data. These data points are saved into respective folders, with seperate image files for each band or related set of bands. For code related to this see `make_training_set.py`.

Various scripts are also required to generate the labels for the model, as the MTBS burned regions are Shapely polygons, and must be rasterized at the resolution of the other data points. Other scripts include those for cropping data to specified coordinates, reprojecting data, and calculating our features from landsat (NDVI, NDMI, BAI, and LST).