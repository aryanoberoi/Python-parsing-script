import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from datetime import datetime
import os

# URL of the webpage you want to parse
URL = "https://www.chittorgarh.com/report/sme-ipo-subscription-status-live-bidding-bse-nse/22/"

# CSV file path
CSV_FILE = "output.csv"

# Function to load existing data from the CSV file
def load_existing_data():
    if os.path.exists(CSV_FILE):
        df_existing = pd.read_csv(CSV_FILE)
        return df_existing
    else:
        # Create an empty DataFrame if the file doesn't exist
        return pd.DataFrame()

# Function to parse the webpage and extract data
def parse_webpage():
    response = requests.get(URL)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find all rows with class "color-green"
    rows = soup.find_all('tr', class_='color-green')
    extracted_data = []

    for row in rows:
        # Extract data from each 'td' element within this row
        data = [td.get_text(strip=True) for td in row.find_all('td')]
        if data:
            # Add a timestamp to each row of data
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            data.insert(0, timestamp)
            extracted_data.append(data)
    
    return extracted_data

# Function to check if a row is new
def is_new_row(new_row, existing_data):
    # Convert existing data to a set of tuples
    existing_set = set(tuple(row[1:]) for row in existing_data.values.tolist())  # Exclude timestamp from comparison
    return tuple(new_row[1:]) not in existing_set  # Exclude timestamp from comparison

# Function to write new rows to CSV file
def write_to_csv(new_rows):
    if new_rows:
        df_existing = load_existing_data()
        
        # Filter new rows
        new_data = [row for row in new_rows if is_new_row(row, df_existing)]
        
        if new_data:
            df_new = pd.DataFrame(new_data, columns=['Timestamp'] + [f'Column{i+1}' for i in range(len(new_data[0]) - 1)])
            
            # Append new data to existing data
            df_result = pd.concat([df_existing, df_new], ignore_index=True)
            
            # Write combined data back to CSV
            df_result.to_csv(CSV_FILE, index=False)
            print("New data added to CSV.")
        else:
            print("No new data found.")
    else:
        print("No data extracted.")

# Main loop to fetch data every 2 minutes
while True:
    print("Parsing webpage...")
    new_data = parse_webpage()
    if new_data:
        write_to_csv(new_data)
    else:
        print("No 'tr' with class 'color-green' found.")
    
    # Wait for 2 minutes before the next fetch
    time.sleep(120)
