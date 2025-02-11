import requests
import pandas as pd
import matplotlib.pyplot as plt

# API endpoint base URL
base_url = "https://yields.llama.fi/chart/"

# List of pool IDs
pool_ids = [
    "66985a81-9c51-46ca-9977-42b4fe7bc6df", #sUSDe pool
    "f981a304-bb6c-45b8-b0c5-fd2f515ad23a", #AAVE v3 USDT pool 
    "aa70268e-4b52-42bf-a116-608b370f9501", #AAVE v3 USDC pool 
    "55b0893b-1dbb-47fd-9912-5e439cd3d511", #USD0++ pool
    "c8a24fee-ec00-4f38-86c0-9f6daebc4225", #DAI DSR pool
    "30347261-b48b-4781-b394-081e630d49a9", #SPDAI Morphl pool
    "32d65ccd-5c07-4b45-8441-98bc86c0720a", #Usual USDC+ Morpho pool
    "e65588a1-27ad-4e20-9232-68a6cfaccf63", #AAVE v3 USDS pool
    "4438dabc-7f0c-430b-8136-2722711ae663", #Fluid USDC pool
    "4e8cc592-c8d5-4824-8155-128ba521e903", #Fluid USDT pool
]

# Fetch data for each pool and store in a dictionary
pool_data = {}
for pool_id in pool_ids:
    url = base_url + pool_id
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if isinstance(data, dict) and 'data' in data:  # Check if data is a dictionary and contains 'data' key
            data = data['data']  # Extract the list of data points
        if isinstance(data, list) and len(data) > 0:  # Check if data is a non-empty list
            pool_data[pool_id] = pd.DataFrame(data)
            # Convert timestamp to datetime and create 'date' column
            if 'timestamp' in data[0]:  # Check if 'timestamp' exists in the first item of the data
                # Create a 'date' column from 'timestamp'
                pool_data[pool_id]['date'] = pd.to_datetime([item['timestamp'] for item in data])  
            else:
                print(f"No 'timestamp' found in data for pool {pool_id}.")
                continue  # Skip this pool if 'timestamp' is not found
        else:
            print(f"Unexpected data format for pool {pool_id}: {data}")  # Print unexpected data format
            pool_data[pool_id] = None  # Store None to indicate error
    else:
        print(f"Error fetching data for pool {pool_id}: {response.status_code}")
        pool_data[pool_id] = None  # Store None to indicate error

# Merge dataframes
merged_df = None
for pool_id, df in pool_data.items():
    if df is not None and not df.empty:  # Check if df is not None and not empty
        df['pool_id'] = pool_id  # Add pool_id column for identification
        if 'date' in df.columns:  # Check if 'date' exists before converting
            df['date'] = pd.to_datetime(df['date'], unit='s').dt.date  # Convert timestamp to date
        df.set_index('date', inplace=True)  # Set date as index
        df = df[['apy', 'tvlUsd']] # Select only apy and tvlUsd columns
        df = df.rename(columns={'apy': f'apy_{pool_id}', 'tvlUsd': f'tvlUsd_{pool_id}'}) # Rename columns to avoid collision

        if merged_df is None:
            merged_df = df
        else:
            merged_df = pd.merge(merged_df, df, left_index=True, right_index=True, how='outer')

if merged_df is None or merged_df.empty:  # Check if merged_df is None or empty
    print("No data fetched successfully. Exiting.")
    exit()

#print dataframe to check if it's correct
print(merged_df.head())
print(merged_df.tail())

# Calculate weighted average APY
apy_cols = [col for col in merged_df.columns if col.startswith('apy_')]
tvl_cols = [col for col in merged_df.columns if col.startswith('tvlUsd_')]

merged_df['weighted_apy'] = 0
total_tvl = merged_df[tvl_cols].sum(axis=1)

for i in range(len(apy_cols)):
    apy_col = apy_cols[i]
    tvl_col = tvl_cols[i]
    merged_df['weighted_apy'] += merged_df[apy_col].fillna(0) * merged_df[tvl_col].fillna(0) # fillna(0) to handle missing values gracefully

merged_df['weighted_apy'] = merged_df['weighted_apy'] / total_tvl.replace(0, 1) # Avoid division by zero if total_tvl is 0, replace 0 with 1 for division

# Calculate 14-day moving average of weighted APY
merged_df['ma_apy_14d'] = merged_df['weighted_apy'].rolling(window=14, min_periods=1).mean()

# Plotting the last 360 days
plot_start_date = merged_df.index[-1] - pd.Timedelta(days=360)
plot_df = merged_df[merged_df.index >= plot_start_date]

plt.figure(figsize=(8, 5), facecolor='#121314')  # Set the figure background color to #121314
plt.plot(plot_df.index, plot_df['weighted_apy'], label='Weighted APY', color='lemonchiffon', alpha=0.3, linewidth=1)  # Set color to lemonchiffon
plt.plot(plot_df.index, plot_df['ma_apy_14d'], label='14-Day Moving Average APY', color='limegreen', linewidth=2)  # Set color to limegreen

plt.title('Weighted APY and 14-Day Moving Average for DeFi Pools', color='#E9FCE5')  # Set title color to #E9FCE5
plt.xlabel('Date', color='#E9FCE5')  # Set x-label color to #E9FCE5
plt.ylabel('APY (%)', color='#E9FCE5')  # Set y-label color to #E9FCE5

# Set the axes background color
plt.gca().set_facecolor('#121314')  # Set axes background color to match figure

# Set tick label colors to #E9FCE5
plt.tick_params(axis='both', colors='#E9FCE5')  # Set tick label colors to #E9FCE5

# Adjust legend properties
legend = plt.legend(facecolor='#121314', edgecolor='#E9FCE5', fontsize='medium', loc='upper left', framealpha=1)  # Set legend background color and text color
for text in legend.get_texts():
    text.set_color('#E9FCE5')  # Set legend text color to #E9FCE5

plt.grid(True, color='#E9FCE5', alpha=0.5)  # Enable the grid with #E9FCE5 color
plt.tight_layout()
plt.show()