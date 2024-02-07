import pandas as pd
import math

def get_coordinates(airport_code, airport_df):
    # Get latitude and longitude for given airport code
    row = airport_df[airport_df['iata_code'] == airport_code].iloc[0]
    return row['latitude_deg'], row['longitude_deg']

def get_flight_coordinates(row, airport_df):
    origin_code = row['origin']  # Assuming column names for simplicity
    destination_code = row['destination']
    
    origin_lat, origin_lng = get_coordinates(origin_code, airport_df)
    destination_lat, destination_lng = get_coordinates(destination_code, airport_df)
    
    return origin_lat, origin_lng, destination_lat, destination_lng


def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate the great-circle distance between two points on the Earth."""
    # Convert latitude and longitude from degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    r = 6371 # Radius of Earth in kilometers
    return c * r


def add_row_to_dataframe(df, values_dict):
    new_row = pd.DataFrame([values_dict])

    df = pd.concat([df, new_row], ignore_index=True)

    return df

def get_column_sum(df, column_name):
    column_sum=df[column_name].sum()
    return column_sum

def surrounded_world(distance):
    surrounded=distance/40030 
    return surrounded

def most_common_value(df, column_name):
    value_counts = df[column_name].value_counts()

    most_common_value = value_counts.idxmax()
    frequency = value_counts.max()
    
    return most_common_value, frequency

if __name__ == "__main__":
    # Code that should only be executed when the script is run directly
    # This could include test code, demonstration code, etc.
    pass