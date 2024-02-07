from src.helpers import *
import pandas as pd
import streamlit as st
from streamlit_option_menu import option_menu
df = pd.read_csv("data/own.csv")
if df["distance"].isnull().any():
    airport_df = pd.read_csv("data/airports.csv")

    df[['origin_lat', 'origin_lng', 'destination_lat', 'destination_lng']] = df.apply(lambda row: get_flight_coordinates(row, airport_df), axis=1, result_type='expand')
    for index, row in df.iterrows():
        if pd.isnull(row['distance']):
            lat1, lon1, lat2, lon2 = row['origin_lat'], row['origin_lng'], row['destination_lat'], row['destination_lng']
            if pd.notnull(lat1) and pd.notnull(lon1) and pd.notnull(lat2) and pd.notnull(lon2):
                df.at[index, 'distance'] = calculate_distance(lat1, lon1, lat2, lon2)
print(df)


st.title("Your Streamlit App")

with st.sidebar:
    selection = option_menu(
        "Tabs",
        [
            "Overview",
            "Add Data"
        ],
        icons=[
            "airplane",
            "cloud-upload"
        ],
        menu_icon="archive",
        default_index=0,
        styles={
            "container": {"padding": "0!important", "width": "100%", "background-color": "#02001e"},
            "icon": {"font-size": "14px", "margin-right": "5px", "color": "white"}, 
            "nav-link": {"font-size": "14px", "text-align": "left", "margin":"2px"},
        }
    )



if selection=="Overview":
    st.write("All flights:", df)
    distance=round(get_column_sum(df, "distance"))
    surrounded=round(surrounded_world(distance),ndigits=2)
    st.write(f"✈️ Total distance flown: {distance}km")
    st.write(f"🌎 Surrounded world {surrounded} times")

if selection=="Add Data":
    st.write("Add a new flight:")
    origin_airport = st.text_input("Origin Airport")
    destination_airport = st.text_input("Destination Airport")
    if st.button("Add"):
        new_row = {"origin": origin_airport, "destination": destination_airport}
        df = add_row_to_dataframe(df, new_row)
        st.write("New flight added:", new_row)
        st.write("All flights:", df)
        df.to_csv("data/own.csv", index=False)
        st.success("successfully uploaded new data")


