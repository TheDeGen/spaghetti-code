import requests
import json
import matplotlib.pyplot as plt
import datetime

def get_historical_tvl(protocol):
  # Retrieves the historical Total Value Locked (TVL) data for a given protocol from the DeFiLlama API.
  api_url = f"https://api.llama.fi/protocol/{protocol}"

  try:
    response = requests.get(api_url)
    response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)

    data = response.json()
    return data.get('tvl')  # returns the list of tvl data points.

  except requests.exceptions.RequestException as e:
    print(f"Error during API request: {e}")
    return None
  except json.JSONDecodeError as e:
    print(f"Error decoding JSON response: {e}")
    return None
  except KeyError as e:
    print(f"Key Error: {e}. The response may not have the expected format.")
    return None
  except Exception as e:
    print(f"An unexpected error occurred: {e}")
    return None


def print_historical_tvl(tvl_data):
  if tvl_data is None:
    print("No TVL data to display.")
    return

  print("Historical TVL data:")
  for entry in tvl_data:
    date = entry.get('date')
    tvl = entry.get('totalLiquidityUSD')  # Changed from 'tvl' to 'totalLiquidityUSD'

    if date is not None and tvl is not None:
      print(f"  Date: {date}, TVL: {tvl}")
    else:
      print(f"  Skipping entry with missing data: {entry}")


def get_protocols():
    num_protocols = int(input("How many protocols do you want to analyze? "))  # New input for number of protocols
    protocols = []  # List to store protocol names

    for _ in range(num_protocols):  # Loop to get protocol names
        protocol_name = input("Enter the name of the protocol: ")  # New input for protocol name
        protocols.append(protocol_name)  # Add protocol name to the list

    return protocols  # Return the list of protocol names


def plot_historical_tvl(all_tvl_data, protocols):
    plt.style.use('dark_background')  # Set the style to dark background
    plt.figure(figsize=(8, 5))  # Adjust figure size for better readability

    # Use the Summer colormap
    colormap = plt.get_cmap("summer")

    # Determine the maximum starting date across all series
    max_start_date = None
    for tvl_data in all_tvl_data:
        if tvl_data:
            start_date = min(entry.get('date') for entry in tvl_data if entry.get('date') is not None)
            if max_start_date is None or start_date > max_start_date:
                max_start_date = start_date

    for i, (tvl_data, protocol_name) in enumerate(zip(all_tvl_data, protocols)):
        if tvl_data:
            dates = []
            tvls = []

            for entry in tvl_data:
                date = entry.get('date')
                tvl = entry.get('totalLiquidityUSD')  # Changed from 'tvl' to 'totalLiquidityUSD'

                if date is not None and tvl is not None and date >= max_start_date:  # Only add if date is after max_start_date
                    dates.append(datetime.datetime.fromtimestamp(date))
                    tvls.append(tvl)

            if dates and tvls:  # Check that we have data before plotting
                plt.plot(dates, tvls, label=protocol_name, color=colormap(i / len(protocols)))  # Use colormap for color

    plt.xlabel("Date")
    plt.ylabel("Total Value Locked (TVL)")
    plt.title("Historical TVL of Protocols")
    plt.grid(True, alpha=0.5)  # Set grid alpha to 0.5 for transparency
    plt.xticks(rotation=45)  # Rotate x-axis labels for readability
    plt.legend()  # Add a legend to differentiate protocols

    # Format y-axis to show commas for thousands
    plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: format(int(x), ',')))

    plt.tight_layout()  # Adjust layout to prevent labels from overlapping
    plt.show()

# Main execution
if __name__ == "__main__":
    protocols = get_protocols()  # Call the function to get protocol names
    all_tvl_data = []  # List to store TVL data for all protocols

    for protocol_name in protocols:  # Iterate over each protocol name
        tvl_data = get_historical_tvl(protocol_name)
        all_tvl_data.append(tvl_data)  # Store the TVL data for each protocol

        if tvl_data:
            print_historical_tvl(tvl_data)
        else:
            print(f"Failed to retrieve historical TVL data for {protocol_name}.")

    plot_historical_tvl(all_tvl_data, protocols)  # Call the plotting function for all protocols
