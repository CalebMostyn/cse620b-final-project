# cse620b-final-project
Random Forest Model for Identifying Wildfire Risk from GIS and Remote Sensing Data 

## Project Structure
project/

├── data/

│   ├── data_points_n.txt       # Definition of N Observations (lat, long, time, etc..)

│   ├── data_point_0/               # Data Files for Observation 0

│   ├── .../                        # ...

│   └── data_point_n/               # Data Files for Observation N

├── scripts/                    # Python Scripts

│   ├── make_training_set.py        # Script to Randomly Generate A Set of N Observations

│   ├── train_model.py              # Trains a Random Forest on Training Data Set

│   └── evaluate_model.py           # Script for Cross-Validation of the Model

├── model/                      # Model Files

├── LICENSE                     # MIT License

└── README.md                   # Project Description

## Data
Training data is sourced from:
- [Landsat 8]{https://landsat.gsfc.nasa.gov/satellites/landsat-8/}
- [MERRA-2]{https://gmao.gsfc.nasa.gov/reanalysis/merra-2/}
- [MODIS]{https://modis.gsfc.nasa.gov/data/}
