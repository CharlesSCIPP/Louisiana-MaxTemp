# Average Maximum Temperature across Louisiana

This repository contains Python scripts for processing NetCDF files and extracting information from them. The scripts are designed to handle climate data in NetCDF format and perform various tasks such as downloading files, processing temperature data, and filtering out rows based on meaningful temperature values.

## Scripts

1. **ncdownloader.py**

    This script facilitates the downloading of NetCDF files for a specified year from the National Centers for Environment Information (NCEI), managed by the National Oceanic and Atmospheric Administration (NOAA). Upon execution, the script prompts the user to input a year, following which it proceeds to download the corresponding NetCDF files to a local directory.

    **Usage:**
    ```bash
    python ncdownloader.py
    ```

2. **LAMaxTempProcessor.py**

    This script specializes in processing downloaded NetCDF files containing temperature data for the state of Louisiana. It computes the daily maximum temperatures for Louisiana from the NetCDF files, performs filtering operations to eliminate rows based on meaningful temperature values, and ultimately saves the processed data to a CSV file.

    **Dependencies:**
    - geopandas
    - xarray
    - numpy
    - pandas
    - shapely

    **Usage:**
    ```bash
    python LAMaxTempProcessor.py
    ```
3. **LARegionsMaxTempProcessor.py**

    This script does same thing as LAMaxTempProcessor.py, but it computes the daily max temperature for regions within the state of Louisiana.

    **Dependencies:**
    - geopandas
    - xarray
    - numpy
    - pandas
    - shapely

    **Usage:**
    ```bash
    python LAMaxTempProcessor.py
    ```

## Environment Setup

To set up the required environment, you can use the provided `environment.yml` file. This file lists all the dependencies needed to run the scripts. You can create a conda environment using this file by executing the following command:

```bash
conda env create -f environment.yml
```

## Data Source

The data utilized in these scripts are maintained by the National Oceanic and Atmospheric Administration’s (NOAA) National Centers for Environment Information (NCEI). For detailed insights into the dataset, reference the paper titled “Daily High-Resolution Temperature and Precipitation Fields for the Contiguous United States from 1951 to Present” authored by Durre et al., (2021).

**Reference:**
Durre, I., Arguez, A., Schreck III, C.J., Squires, M.F. and Vose, R.S., 2022. Daily high-resolution temperature and precipitation fields for the contiguous United States from 1951 to present. Journal of Atmospheric and Oceanic Technology, 39(12), pp.1837-1855.

## Data Caveats

- State-wide daily temperature estimates are derived by averaging all grids within the state boundary (Census TIGER/Line Shapefiles) of Louisiana.
- Daily values represent prevailing conditions during the 24 hours ending in the morning on the observation day. For instance, the estimates for April 1st reflect conditions from the morning of March 31st through the morning of April 1st. The data typically exhibit a latency of 1-3 days, and preliminary estimates may undergo alterations.

## Credit

Credit for code development and testing can be attributed to the Southern Climate Impacts Planning Program ([https://www.southernclimate.org/](https://www.southernclimate.org/)). The authors of these scripts are Charles Simson and Vincent Brown.

## License

These scripts are provided under the MIT License. You can find the license terms in the LICENSE file included in the repository.

