from src.helpers import *
import pandas as pd
import streamlit as st
from streamlit_option_menu import option_menu
from streamlit_folium import st_folium
import matplotlib.pyplot as plt
import folium
st.set_option('deprecation.showPyplotGlobalUse', False)
#df = pd.read_csv("data/own.csv")
df=pd.read_csv("data/kolj2.csv")
airport_df = pd.read_csv("data/airports.csv")
if df["distance"].isnull().any():
    df[['origin_lat', 'origin_lng', 'destination_lat', 'destination_lng']] = df.apply(lambda row: get_flight_coordinates(row, airport_df), axis=1, result_type='expand')
    for index, row in df.iterrows():
        if pd.isnull(row['distance']):
            lat1, lon1, lat2, lon2 = row['origin_lat'], row['origin_lng'], row['destination_lat'], row['destination_lng']
            if pd.notnull(lat1) and pd.notnull(lon1) and pd.notnull(lat2) and pd.notnull(lon2):
                df.at[index, 'distance'] = calculate_distance(lat1, lon1, lat2, lon2)
                df.to_csv("data/kolj2.csv", index=False)
## update origin link if necessary
if df["origin_link"].isnull().any():
    update_links(df, airport_df, origin_col="origin", link_col="origin_link", second_origin_col="ident", second_link_col="home_link")
    df.to_csv("data/kolj2.csv", index=False)
if df["destination_link"].isnull().any():
    update_links(df, airport_df, origin_col="destination", link_col="destination_link", second_origin_col="ident", second_link_col="home_link")
    df.to_csv("data/kolj2.csv", index=False)
if df["origin_wikipedia_link"].isnull().any():
    update_links(df, airport_df, origin_col="origin", link_col="origin_wikipedia_link", second_origin_col="ident", second_link_col="wikipedia_link")
    df.to_csv("data/kolj2.csv", index=False)
if df["destination_wikipedia_link"].isnull().any():
    update_links(df, airport_df, origin_col="destination", link_col="destination_wikipedia_link", second_origin_col="ident", second_link_col="wikipedia_link")
    df.to_csv("data/kolj2.csv", index=False)

print(df)


#st.title("Your Streamlit App")

with st.sidebar:
    selection = option_menu(
        "Tabs",
        [
            "Overview",
            "Map",
            "More Statistics",
            "Add Data"
            
        ],
        icons=[
            "airplane",
            "map",
            "bar-chart",
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
    st.title("Overview")
    st.write("All flights:", df)
    distance=round(get_column_sum(df, "distance"))
    surrounded=round(surrounded_world(distance),ndigits=2)
    st.write(f"✈️ Total distance flown: {distance}km")
    st.write(f"🌎 Surrounded world {surrounded} times")


if selection == "Map":
    # Your code to display the map
    st.title('Map')
    m = folium.Map(location=[df['origin_lat'].mean(), df['origin_lng'].mean()], zoom_start=2)

    # Add lines and markers for each origin-destination pair
    for _, row in df.iterrows():
        # Origin marker
        folium.Marker(
            location=[row['origin_lat'], row['origin_lng']],
            icon=folium.Icon(color='blue', icon='plane-departure'),
            popup='Origin'
        ).add_to(m)
        
        # Destination marker
        folium.Marker(
            location=[row['destination_lat'], row['destination_lng']],
            icon=folium.Icon(color='green', icon='plane-arrival'),
            popup='Destination'
        ).add_to(m)
        
        # Line connecting origin and destination
        folium.PolyLine(
            locations=[
                [row['origin_lat'], row['origin_lng']],
                [row['destination_lat'], row['destination_lng']]
            ],
            color='red'
        ).add_to(m)

    # Assuming `m` is your folium Map object from previous examples
    st_folium(m, width=725, height=500)


if selection=="More Statistics":
    st.title("More Statistics")
    origin_counts = df['origin'].value_counts()
    destination_counts = df['destination'].value_counts()

    # Create two columns layout
    col1, col2 = st.columns(2)

    # Display the bar chart for origin values in the first column
    with col1:
        st.subheader("Distribution of Origin Airports")
        plt.bar(origin_counts.index, origin_counts.values, color='blue')
        plt.xlabel('Airport')
        plt.ylabel('Occurrences')
        plt.xticks(rotation=90)
        plt.yticks(range(0, max(origin_counts.values) + 1, 1)) 
        st.pyplot()

    # Display the bar chart for destination values in the second column
    with col2:
        st.subheader("Distribution of Destination Airports")
        plt.bar(destination_counts.index, destination_counts.values, color='red')
        plt.xlabel('Airport')
        plt.ylabel('Occurrences')
        plt.xticks(rotation=90)
        plt.yticks(range(0, max(origin_counts.values) + 1, 1)) 
        st.pyplot()


if selection == "Add Data":
    st.title("Add Data")
    st.write("Add a new flight:")
    airline = st.text_input("Airline", placeholder="Lufthansa")
    aircraft = st.text_input("Aircraft", placeholder="B747-8i")
    registration = st.text_input("Registration", placeholder="D-ABYF")
    seat = st.text_input("Seat", placeholder="1A")
    flight_number = st.text_input("Flight Number", placeholder="LH 430")
    origin_airport = st.text_input("Origin Airport", placeholder="EDDF")
    destination_airport = st.text_input("Destination Airport", placeholder="KORD")
    date = st.text_input("Date", placeholder="05.06.2004")
    origin_address = st.text_input("Origin Address", placeholder="Frankfurt Arpt (FRA), 60547 Frankfurt am Main, Germany")
    destination_address = st.text_input("Destination Address", placeholder="O'Hare International Airport (ORD), 10000 W Balmoral Ave, Chicago, IL 60666, USA")
    
    if st.button("Add"):
        new_row = {
            "Airline": airline,
            "Aircraft": aircraft,
            "Regestration": registration,
            "Seat": seat,
            "Flight Number": flight_number,
            "origin": origin_airport,
            "destination": destination_airport,
            "Date": date,
            "Origin Address": origin_address,
            "Destination Address": destination_address
        }
        df = add_row_to_dataframe(df, new_row)
        st.write("New flight added:", new_row)
        st.write("All flights:", df)
        df.to_csv("data/kolj2.csv", index=False)
        st.success("successfully uploaded new data")




