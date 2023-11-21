import os
import requests
import json
import pandas as pd
from datetime import datetime

headers = {'Content-type': 'application/json'}

# Define the series IDs and their mappings
series_mappings = {
    'CUUR0000SA0': 'CPI-U All Items',
    'CUUR0000SA0L1E': 'CPI x Food_Energy',
    'CUUR0000SETA01': 'New Vehicles',
    'CUSR0000SETA02': 'Used Vehicles',
    'CUSR0000SETD': 'Auto Body Work',
    'CUSR0000SEMD': 'Hospital',
    'CUSR0000SAM2': 'Professional Care',
    'CUUR0000SAM1': 'RX_Equipment',
}

# Get today's date to determine the end year
today = datetime.today()
end_year = today.year

# Define the start and end years
start_year = 2021

# Prepare the data payload for the API request
data = json.dumps({"seriesid": list(series_mappings.keys()), "startyear": str(start_year), "endyear": str(end_year)})
p = requests.post('https://api.bls.gov/publicAPI/v2/timeseries/data/', data=data, headers=headers)

json_data = json.loads(p.text)

# Initialize a dictionary to store the data for each series
series_data = {series_name: [] for series_name in series_mappings.values()}

for series in json_data['Results']['series']:
    series_id = series['seriesID']
    series_name = series_mappings.get(series_id, "Unknown")

    for item in series['data']:
        year = item['year']
        period = item['period']
        value = item['value']

        # Check if the period is within the desired range (2021 to 2023)
        if start_year <= int(year) <= end_year and 'M01' <= period <= 'M12':
            # Append the data to the corresponding series
            series_data[series_name].append((year, period, value))

# Create separate DataFrames for each series
dfs = [pd.DataFrame(data, columns=['year', 'period', series_name]) for series_name, data in series_data.items()]

# Merge the DataFrames on 'year' and 'period'
merged_df = pd.concat(dfs, axis=1)

# Remove redundant 'year' and 'period' columns
merged_df = merged_df.loc[:, ~merged_df.columns.duplicated()]

# Save the merged DataFrame to an Excel file
export_location = r'<<SAVE LOC>>'
excel_filename = os.path.join(export_location, "economic_data_sheets_cleaned.xlsx")
merged_df.to_excel(excel_filename, index=False)

print(f"Data exported to {excel_filename}")
