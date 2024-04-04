"""
Author: Charles Simson
Affiliation: Southern Climate Impacts Planning Program
Date of Code Release: 03/04/2024
"""

import os
import requests
from urllib.parse import urlparse

# Function to validate the file name
def validate_file_name(file_name):
    return file_name.startswith("ncdd-") and (file_name.endswith("-grd-scaled.nc") or file_name.endswith("-grd-prelim.nc"))

# Function to download files for a given year
def download_files_for_year(year):
    # Define the URL where the files are located
    base_url = f"https://www.ncei.noaa.gov/data/nclimgrid-daily/access/grids/{year}/"

    # Send a request to the URL to get the HTML content
    response = requests.get(base_url)

    if response.status_code == 200:
        # Parse the HTML content to extract links to files with ".nc" extension
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find all anchor tags with href attribute ending with ".nc"
        nc_file_links = [a['href'] for a in soup.find_all('a', href=True) if a['href'].endswith('.nc')]
        
        # Create a directory to save the downloaded files
        download_dir = f"downloaded_nc_files_{year}"
        os.makedirs(download_dir, exist_ok=True)
        
        # Download each ".nc" file
        for nc_file_link in nc_file_links:
            # Build the full URL of the file
            file_url = base_url + nc_file_link
            
            # Extract the file name from the URL
            file_name = os.path.basename(urlparse(file_url).path)
            
            # Check if the file name matches the expected pattern
            if validate_file_name(file_name):
                # Define the local file path where you want to save the downloaded file
                local_file_path = os.path.join(download_dir, file_name)
                
                # Download the file from the URL and save it locally
                response = requests.get(file_url)
                
                if response.status_code == 200:
                    with open(local_file_path, "wb") as f:
                        f.write(response.content)
                    print(f"Downloaded file saved to {local_file_path}")
                else:
                    print(f"Failed to download {file_name}")
            else:
                print(f"Skipping file {file_name} as it does not match the expected naming pattern.")
    else:
        print("Failed to fetch the URL.")

# Input the year
year = input("Enter the year: ")

# Download files for the specified year
download_files_for_year(year)
