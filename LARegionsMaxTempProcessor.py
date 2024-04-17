"""
Author: Charles Simson
Affiliation: Southern Climate Impacts Planning Program
Date of Code Release: 04/17/2024
"""

import geopandas as gpd
import xarray as xr
import numpy as np
from shapely.geometry import Point
import pandas as pd
import os

# Create an empty DataFrame to store the combined data
combined_df = None

# Directory containing NetCDF files
nc_files_directory = "downloaded_nc_files_2024"

shapefile = gpd.read_file("tl_rd22_us_county/tl_rd22_us_county.shp")

parishes_to_regions = {
    "Southeast": {
        "22051": "Jefferson Parish",
        "22071": "Orleans Parish",
        "22075": "Plaquemines Parish",
        "22087": "St. Bernard Parish",  
    },
    "Capital_Region": {
        "22005": "Ascension Parish",
        "22033": "East Baton Rouge Parish",
        "22047": "Iberville Parish",
        "22077": "Pointe Coupee Parish",
        "22121": "West Baton Rouge Parish",
        "22125": "West Feliciana Parish",
        "22037": "East Feliciana Parish",
    },
    "South_Central_Region": {
        "22057": "Lafourche Parish",
        "22109": "Terrebonne Parish",
        "22101": "St. Mary Parish",
        "22007": "Assumption Parish",
        "22095": "St. John the Baptist Parish",
        "22093": "St. James Parish",
        "22089": "St. Charles Parish",
    },
    "Acadiana": {
        "22001": "Acadia Parish",
        "22039": "Evangeline Parish",
        "22045": "Iberia Parish",
        "22055": "Lafayette Parish",
        "22097": "St. Landry Parish",
        "22113": "Vermilion Parish",
        "22099": "St. Martin Parish",
    },
    "Southwest": {
        "22003": "Allen Parish",
        "22011": "Beauregard Parish",
        "22019": "Calcasieu Parish",
        "22023": "Cameron Parish",
        "22053": "Jefferson Davis Parish",
    },
    "Central": {
        "22009": "Avoyelles Parish",
        "22025": "Catahoula Parish",
        "22029": "Concordia Parish",
        "22043": "Grant Parish",
        "22059": "LaSalle Parish",
        "22079": "Rapides Parish",
        "22115": "Vernon Parish",
        "22127": "Winn Parish",
    },
    "Northeast": {
        "22021": "Caldwell Parish",
        "22035": "East Carroll Parish",
        "22041": "Franklin Parish",
        "22065": "Madison Parish",
        "22067": "Morehouse Parish",
        "22073": "Ouachita Parish",
        "22083": "Richland Parish",
        "22111": "Union Parish",
        "22123": "West Carroll Parish",
        "22049": "Jackson Parish",
        "22061": "Lincoln Parish",
        "22107": "Tensas Parish",
    },
    "Northshore": {
        "22091": "St. Helena Parish",
        "22063": "Livingston Parish",
        "22117": "Washington Parish",
        "22103": "St. Tammany Parish",
        "22105": "Tangipahoa Parish",
    },
    "Northwest": {
        "22017": "Caddo Parish",
        "22015": "Bossier Parish",
        "22119": "Webster Parish",
        "22027": "Claiborne Parish",
        "22081": "Red River Parish",
        "22013": "Bienville Parish",
        "22085": "Sabine Parish",
        "22069": "Natchitoches Parish",
        "22031": "De Soto Parish",
    }
}

# Loop through each NetCDF file in the directory
for filename in os.listdir(nc_files_directory):
    if filename.endswith(".nc"):
        # Open the current NetCDF file
        nc_file = xr.open_dataset(os.path.join(nc_files_directory, filename))

        # Initialize a dictionary to store daily maximum temperatures for regions
        region_daily_max_temps = {}

        # Loop over regions and their associated parishes
        for region, parishes in parishes_to_regions.items():
            print(f"Calculating daily maximum temperatures for {region} in {filename}...")

            # Initialize an empty boolean mask with the same dimensions as the netCDF file
            mask = np.zeros_like(nc_file["tmax"].values, dtype=bool)

            # Loop over parishes in the current region
            for parish_id in parishes.keys():
                # Get the geometry for the parish
                parish_geometry = shapefile[shapefile['GEOID'] == parish_id].geometry.values[0]

                # Extract latitude and longitude values from the netCDF file
                lats = nc_file['lat'].values
                lons = nc_file['lon'].values

                # Create a boolean mask using the parish geometry
                for i in range(len(lats)):
                    for j in range(len(lons)):
                        if parish_geometry.contains(Point(lons[j], lats[i])):
                            mask[:, i, j] = True

            # Use the mask to subset the grid data for the region
            grid_subset = nc_file["tmax"].where(mask)

            # Calculate the daily maximum temperature for the region
            daily_maximum_tmax_region_celsius = grid_subset.mean(dim=['lat', 'lon'])

            # Convert Celsius to Fahrenheit
            daily_maximum_tmax_region_fahrenheit = (daily_maximum_tmax_region_celsius * (9/5)) + 32

            # Store the daily maximum temperature in Fahrenheit in the dictionary
            region_daily_max_temps[region] = daily_maximum_tmax_region_fahrenheit

            print(f"Finished calculating daily maximum temperatures for {region} in {filename}.")

        # Close the current NetCDF file
        nc_file.close()

        # Convert the region_daily_max_temps dictionary to a DataFrame
        df = pd.DataFrame(region_daily_max_temps)

        # Add a 'Date' column to the DataFrame
        dates = nc_file['time'].values
        df.insert(0, 'Date', dates)

        # Combine the data with the previously collected data
        if combined_df is None:
            combined_df = df
        else:
            combined_df = pd.concat([combined_df, df], ignore_index=True)

# Sort the DataFrame by the 'Date' column in ascending order
combined_df = combined_df.sort_values('Date')

# Save the combined DataFrame to a CSV file
combined_df.to_csv("combined_region_daily_max_temps_F.csv", index=False)
