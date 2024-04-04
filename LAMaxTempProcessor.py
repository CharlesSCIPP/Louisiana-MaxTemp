"""
Author: Charles Simson
Affiliation: Southern Climate Impacts Planning Program
Date of Code Release: 03/04/2024
"""

# Import necessary libraries
import geopandas as gpd
import xarray as xr
import numpy as np
from shapely.geometry import Point
import pandas as pd
import os
import multiprocessing
from functools import partial
import time

# Define a function to process each NetCDF file
def process_nc_file(filename, state_shapefile):
    # Print the filename being processed
    print(f"Processing {filename}...")
    
    # Record the start time
    start_time = time.time()
    
    # Open the NetCDF file
    nc_file = xr.open_dataset(filename)

    # Initialize dictionary to store daily max temperatures
    daily_max_temps = {}

    # Extract state geometry for Louisiana
    state_geometry = state_shapefile[state_shapefile['GEOID'] == '22'].geometry.values[0]

    # Extract latitude and longitude values from the NetCDF file
    lats = nc_file['lat'].values
    lons = nc_file['lon'].values

    # Initialize a mask for the entire state of Louisiana
    mask = np.zeros_like(nc_file["tmax"].values, dtype=bool)
    
    # Check if each grid point is within the state geometry and update the mask accordingly
    for i in range(len(lats)):
        for j in range(len(lons)):
            if state_geometry.contains(Point(lons[j], lats[i])):
                mask[:, i, j] = True

    # Apply the mask to extract grid points within the state and calculate mean daily maximum temperature
    grid_subset = nc_file["tmax"].where(mask)
    daily_max_tmax_state_celsius = grid_subset.mean(dim=['lat', 'lon'])
    daily_max_tmax_state_fahrenheit = (daily_max_tmax_state_celsius * (9/5)) + 32

    # Store the daily maximum temperatures for the state
    daily_max_temps['Louisiana'] = daily_max_tmax_state_fahrenheit

    # Close the NetCDF file
    nc_file.close()

    # Convert the temperature data to DataFrame
    df = pd.DataFrame(daily_max_temps)
    
    # Extract dates from the NetCDF file and insert them as the first column in the DataFrame
    dates = nc_file['time'].values
    df.insert(0, 'Date', dates)

    # Record the end time and print processing time
    end_time = time.time()
    print(f"Finished processing {filename} in {end_time - start_time:.2f} seconds")
    
    # Return the DataFrame along with start and end dates
    return df, dates[0], dates[-1]

# Main block of code
if __name__ == '__main__':
    # Directory containing NetCDF files
    nc_files_directory = "downloaded_nc_files"

    # Load shapefile for Louisiana state
    state_shapefile = gpd.read_file("tl_rd22_us_state/tl_rd22_us_state.shp")

    # Define a partial function with fixed parameters for multiprocessing
    process_func = partial(process_nc_file, state_shapefile=state_shapefile)

    # Get list of filenames and sort them based on the month
    filenames = [os.path.join(nc_files_directory, filename) for filename in os.listdir(nc_files_directory) if filename.endswith(".nc")]
    filenames.sort(key=lambda x: int(x.split('-')[1]))  # Sort by month assuming the filename format is consistent

    # Define the number of processes to use
    num_processes = multiprocessing.cpu_count()  # or specify the number of processes you want to use

    # Create a pool of worker processes
    with multiprocessing.Pool(processes=num_processes) as pool:
        # Map the process function over the list of filenames and execute them in parallel
        results = pool.map(process_func, filenames)

    # Concatenate all the results into a single DataFrame
    combined_df = pd.concat([result[0] for result in results], ignore_index=True)

    # Sort the DataFrame by the 'Date' column in ascending order
    combined_df = combined_df.sort_values('Date')

    # Define the minimum and maximum meaningful temperature values (in Fahrenheit)
    min_temp = -100  # Example minimum meaningful temperature
    max_temp = 150   # Example maximum meaningful temperature

    # Filter rows based on meaningful temperature values
    filtered_indices = ((combined_df['Louisiana'] < min_temp) | (combined_df['Louisiana'] > max_temp))
    filtered_rows = combined_df[filtered_indices]

    # Print out filtered rows and the reason for filtering
    if not filtered_rows.empty:
        print("Filtered out rows:")
        for date, row in filtered_rows[['Date', 'Louisiana']].itertuples(index=False):
            print(f"Row for date {date} with temperature value {row} was not added because it's outside the meaningful temperature range.")
    else:
        print("No rows were filtered out.")

    # Filter the DataFrame
    combined_df_filtered = combined_df[~filtered_indices]

    # Extract the start and end dates from the results
    start_date = min(result[1] for result in results)
    end_date = max(result[2] for result in results)

    # Convert numpy.datetime64 to Python datetime objects
    start_date = pd.Timestamp(start_date).to_pydatetime()
    end_date = pd.Timestamp(end_date).to_pydatetime()

    # Extract the start and end dates
    start_date_str = start_date.strftime('%Y-%m-%d')
    end_date_str = end_date.strftime('%Y-%m-%d')

    # Define the filename with start and end dates
    filename = f"combined_Louisiana_state_daily_max_temps_F_{start_date_str}_to_{end_date_str}.csv"

    # Save the filtered DataFrame to a CSV file
    combined_df_filtered.to_csv(filename, index=False)


