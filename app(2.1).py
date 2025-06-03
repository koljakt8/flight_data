from src.helpers import *
import pandas as pd
import streamlit as st
from streamlit_option_menu import option_menu
from streamlit_folium import st_folium
import matplotlib.pyplot as plt
import folium
st.set_option('deprecation.showPyplotGlobalUse', False)
#df = pd.read_csv("data/own.csv")
df=pd.read_csv("data/personal_flight_data.csv")
airport_df = pd.read_csv("data/airports.csv")
leaf_keywords_df = pd.read_csv("data/green_aircraft.csv")
leaf_keywords = [str(k).strip().lower() for k in leaf_keywords_df["keyword"].dropna()]
airline_colors_df = pd.read_csv("data/airline_colors.csv")
airline_color_dict = dict(zip(airline_colors_df['Airline'], airline_colors_df['Color']))
updates_made = False
if df["distance"].isnull().any():
    for index, row in df.iterrows():
        # Only process if both origin and destination are present
        if pd.notnull(row.get('origin', None)) and pd.notnull(row.get('destination', None)) and row['origin'] and row['destination']:
            # Try to find airport by ICAO or IATA code
            def find_airport(code):
                if pd.isnull(code):
                    return None
                code = str(code).strip().upper()
                # Try ICAO first
                match = airport_df[airport_df['ident'].str.upper() == code]
                if not match.empty:
                    return match.iloc[0]
                # Try IATA if available
                if 'iata_code' in airport_df.columns:
                    match = airport_df[airport_df['iata_code'].str.upper() == code]
                    if not match.empty:
                        return match.iloc[0]
                return None

            # Fill coordinates if missing
            if pd.isnull(row['origin_lat']) or pd.isnull(row['origin_lng']) or pd.isnull(row['destination_lat']) or pd.isnull(row['destination_lng']):
                # Use helper to get coordinates, but allow both ICAO and IATA
                origin_airport = find_airport(row['origin'])
                dest_airport = find_airport(row['destination'])
                if origin_airport is not None and dest_airport is not None:
                    df.at[index, 'origin_lat'] = origin_airport['latitude_deg']
                    df.at[index, 'origin_lng'] = origin_airport['longitude_deg']
                    df.at[index, 'destination_lat'] = dest_airport['latitude_deg']
                    df.at[index, 'destination_lng'] = dest_airport['longitude_deg']
                    updates_made = True
            # Fill distance if missing and coordinates are present
            lat1, lon1, lat2, lon2 = df.at[index, 'origin_lat'], df.at[index, 'origin_lng'], df.at[index, 'destination_lat'], df.at[index, 'destination_lng']
            if pd.isnull(row['distance']) and pd.notnull(lat1) and pd.notnull(lon1) and pd.notnull(lat2) and pd.notnull(lon2):
                df.at[index, 'distance'] = calculate_distance(lat1, lon1, lat2, lon2)
                updates_made = True
        else:
            # If origin or destination is missing, leave coordinates and distance as NaN
            continue
## update origin link if necessary
if df["origin_link"].isnull().any():
    update_links(df, airport_df, origin_col="origin", link_col="origin_link", second_origin_col="ident", second_link_col="home_link")
    updates_made = True
if df["destination_link"].isnull().any():
    update_links(df, airport_df, origin_col="destination", link_col="destination_link", second_origin_col="ident", second_link_col="home_link")
    updates_made = True
if df["origin_wikipedia_link"].isnull().any():
    update_links(df, airport_df, origin_col="origin", link_col="origin_wikipedia_link", second_origin_col="ident", second_link_col="wikipedia_link")
    updates_made = True
if df["destination_wikipedia_link"].isnull().any():
    update_links(df, airport_df, origin_col="destination", link_col="destination_wikipedia_link", second_origin_col="ident", second_link_col="wikipedia_link")
    updates_made = True

if updates_made:
    df.to_csv("data/personal_flight_data.csv", index=False)
print(df)


#st.title("Your Streamlit App")

with st.sidebar:
    selection = option_menu(
        "Tabs",
        [
            "Overview",
            "Map",
            "More Statistics",
            "Add Data",
            "Edit Data",
            "Information"  # <-- Add this line
        ],
        icons=[
            "airplane",
            "map",
            "bar-chart",
            "cloud-upload",
            "pencil-square",
            "info-circle"  # <-- Add an icon for Information
        ],
        menu_icon="archive",
        default_index=0,
        styles={
            "container": {"padding": "0!important", "width": "100%", "background-color": "#02001e"},
            "icon": {"font-size": "14px", "margin-right": "5px", "color": "white"}, 
            "nav-link": {"font-size": "14px", "text-align": "left", "margin":"2px"},
        }
    )


if selection == "Overview":
    st.title("All your flights add up:")

    # 📅 Sort by date (most recent first)
    df_sorted = df.copy()
    df_sorted['Date'] = pd.to_datetime(df_sorted['Date'], dayfirst=True, errors='coerce')
    df_sorted = df_sorted.sort_values(by='Date', ascending=False)

    # 📅 Extract valid dates
    valid_dates = df_sorted['Date'].dropna()

    # Calculate streak
    if st.session_state.get("monthly_streak", False):
        # Monthly streak
        months = valid_dates.dt.to_period("M").sort_values(ascending=False).unique()
        streak = 1
        for i in range(1, len(months)):
            if months[i] == months[i - 1] - 1:
                streak += 1
            else:
                break
        if streak == 1:
            streak_text = f"{months[0].strftime('%b %Y')}"
        else:
            streak_text = f"{months[streak - 1].strftime('%b %Y')} → {months[0].strftime('%b %Y')}"
        streak_label = "month"
    else:
        # Yearly streak (default)
        years = valid_dates.dt.year.sort_values(ascending=False).unique()
        streak = 1
        for i in range(1, len(years)):
            if years[i] == years[i - 1] - 1:
                streak += 1
            else:
                break
        if streak == 1:
            streak_text = f"{years[0]}"
        else:
            streak_text = f"{years[streak - 1]} → {years[0]}"
        streak_label = "year"

    # 🎯 Display streak at the top, centered, and larger
    st.markdown(
        f"""
        <div style="text-align:center; margin-bottom: 30px;">
            <span style="font-size: 2.8em; font-weight: bold;">🔥 {streak} {streak_label}{'s' if streak > 1 else ''} in a row</span><br>
            <span style="font-size: 1.5em; color: #888;">({streak_text})</span>
        </div>
        """,
        unsafe_allow_html=True
    )

    # ✈️ Statistics
    distance = round(get_column_sum(df, "distance"))
    surrounded = round(surrounded_world(distance), ndigits=2)
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"<span style='font-size:1.6em;'>✈️ Impressive you already covered <b>{distance}</b> km</span>", unsafe_allow_html=True)
        st.markdown(f"<span style='font-size:1.6em;'>🌎 Surrounded world <b>{surrounded}</b> times</span>", unsafe_allow_html=True)

    with col2:
        # Most flown airline
        if not df['Airline'].dropna().empty:
            most_airline = df['Airline'].mode()[0]
            airline_count = df['Airline'].value_counts()[most_airline]
            st.markdown(f"<span style='font-size:1.6em;'>You really seem to love <b>{most_airline}</b> ❤️ ({airline_count} flights)</span>", unsafe_allow_html=True)
        else:
            st.markdown("<span style='font-size:1.6em;'>Most flown airline: N/A</span>", unsafe_allow_html=True)

        # Most flown aircraft
        if not df['Aircraft'].dropna().empty:
            most_aircraft = df['Aircraft'].mode()[0]
            aircraft_count = df['Aircraft'].value_counts()[most_aircraft]
            st.markdown(f"<span style='font-size:1.6em;'>One aircraft stands out, the <b>{most_aircraft}</b> ({aircraft_count} flights)</span>", unsafe_allow_html=True)
        else:
            st.markdown("<span style='font-size:1.6em;'>Most flown aircraft: N/A</span>", unsafe_allow_html=True)

    st.write("---")
    # 🔝 Show the 5 most recent flights


    st.subheader("🆕 Most Recent Flights")
    
    for idx, row in df_sorted.head(5).iterrows():
        aircraft = row.get('Aircraft', '')
        leaf = ""
        if isinstance(aircraft, str) and any(kw in aircraft.lower() for kw in leaf_keywords):
            leaf = " 🍃"
        date_str = row['Date'].strftime('%d.%m.%Y') if pd.notnull(row['Date']) else "Unknown date"
        # Determine color based on airline, fallback to gray if not found or missing
        airline = row.get('Airline', None)
        if pd.notnull(airline):
            airline_key = airline.strip()
            bg_color = airline_color_dict.get(airline_key, "#AAAAAA")
        else:
            bg_color = "#AAAAAA"  # gray for unknown or missing airline

        st.markdown(
            f"""
            <div style="background-color:{bg_color};padding:10px;border-radius:8px;margin-bottom:8px;color:white;">
                <b>{date_str}</b> — {row['Airline']} {row['Flight Number']}
                from {row['origin']} to {row['destination']} on a {row['Aircraft']}
                ({row['Seat']}, {row['Regestration']}){leaf}
            </div>
            """,
            unsafe_allow_html=True
        )

    # 👇 Show/hide older flights with a button
    if "show_older" not in st.session_state:
        st.session_state.show_older = False

    if st.session_state.show_older:
        if st.button("Hide Older Flights", key="hide_older"):
            st.session_state.show_older = False
            st.experimental_rerun()
        st.subheader("📋 Older Flights")
        for idx, row in df_sorted.iloc[5:].iterrows():
            aircraft = row.get('Aircraft', '')
            leaf = ""
            if isinstance(aircraft, str) and any(kw in aircraft.lower() for kw in leaf_keywords):
                leaf = " 🍃"
            date_str = row['Date'].strftime('%d.%m.%Y') if pd.notnull(row['Date']) else "Unknown date"
            airline = row.get('Airline', None)
            if pd.notnull(airline):
                airline_key = airline.strip()
                bg_color = airline_color_dict.get(airline_key, "#AAAAAA")
            else:
                bg_color = "#AAAAAA"

            st.markdown(
                f"""
                <div style="background-color:{bg_color};padding:10px;border-radius:8px;margin-bottom:8px;color:white;">
                    <b>{date_str}</b> — {row['Airline']} {row['Flight Number']}
                    from {row['origin']} to {row['destination']} on a {row['Aircraft']}
                    ({row['Seat']}, {row['Regestration']}){leaf}
                </div>
                """,
                unsafe_allow_html=True
            )
    else:
        if st.button("Show Older Flights", key="show_older"):
            st.session_state.show_older = True
            st.experimental_rerun()
        





if selection == "Map":
    st.title('Map')
    m = folium.Map(location=[df['origin_lat'].mean(), df['origin_lng'].mean()], zoom_start=2)

    for _, row in df.iterrows():
        # Skip if origin or destination is missing or NaN
        if (
            pd.isnull(row.get('origin_lat')) or pd.isnull(row.get('origin_lng')) or
            pd.isnull(row.get('destination_lat')) or pd.isnull(row.get('destination_lng'))
        ):
            continue

        folium.Marker(
            location=[row['origin_lat'], row['origin_lng']],
            icon=folium.Icon(color='blue', icon='plane-departure'),
            popup='Origin'
        ).add_to(m)
        
        folium.Marker(
            location=[row['destination_lat'], row['destination_lng']],
            icon=folium.Icon(color='blue', icon='plane-arrival'),
            popup='Destination'
        ).add_to(m)
        
        folium.PolyLine(
            locations=[
                [row['origin_lat'], row['origin_lng']],
                [row['destination_lat'], row['destination_lng']]
            ],
            color='red'
        ).add_to(m)

    st_folium(m, width=725, height=500)


if selection == "More Statistics":
    st.title("Even more statistics")

    # Prepare statistics
    origin_counts = df['origin'].value_counts()
    destination_counts = df['destination'].value_counts()
    aircraft_counts = df['Aircraft'].value_counts()
    airline_counts = df['Airline'].value_counts()

    def render_stat_blocks(title, counts, color="#4F8BF9", label="Flights"):
        st.subheader(title)
        max_count = counts.max() if not counts.empty else 1
        for item, count in counts.items():
            block_count = min(count, 40)
            bar = f"<span style='display:inline-block;background:{color};height:24px;width:{block_count*10}px;border-radius:6px;'></span>"
            st.markdown(
                f"""
                <div style="display:flex;align-items:center;margin-bottom:8px;">
                    <span style="min-width:120px;font-weight:bold;">{item}</span>
                    {bar}
                    <span style="margin-left:12px;font-size:1.1em;color:#555;'>{count} {label}</span>
                </div>
                """,
                unsafe_allow_html=True
            )
        st.write("---")

    # Arrange two statistics side by side, then the next two below
    col1, col2 = st.columns(2)
    with col1:
        render_stat_blocks("Most Flown Airlines", airline_counts, color="#1590ba", label="Flights")       
    with col2:
        render_stat_blocks("Most Flown Aircraft", aircraft_counts, color="#040086", label="Flights")      

    col3, col4 = st.columns(2)
    with col3:
        render_stat_blocks("Most departure Airports", origin_counts, color="#c41a1a", label="Departures")      
    with col4:
        render_stat_blocks("Most destination Airports", destination_counts, color="#c41a5a", label="Arrivals")
        


if selection == "Add Data":
    st.title("Add Data")
    st.write("Add a new flight:")
    airline = st.text_input("Airline", placeholder="Lufthansa")
    aircraft = st.text_input("Aircraft", placeholder="B747-8i")
    registration = st.text_input("Registration", placeholder="D-EEGL")
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
        #st.write("New flight added:", new_row)
        #st.write("All flights:", df)
        df.to_csv("data/personal_flight_data.csv", index=False)
        st.success("Flights keep flying in!")

if selection == "Edit Data":
    st.title("Edit Flight Data")
    st.write("Select a flight to edit:")

    # Create a summary string for each flight for easier selection
    df_sorted = df.copy()
    df_sorted['Date'] = pd.to_datetime(df_sorted['Date'], dayfirst=True, errors='coerce')
    df_sorted = df_sorted.sort_values(by='Date', ascending=False)
    flight_options = [
        f"{i}: {row['Date'].strftime('%d.%m.%Y') if pd.notnull(row['Date']) else 'Unknown date'} | {row['Airline']} {row['Flight Number']} | {row['origin']} → {row['destination']}"
        for i, row in df_sorted.iterrows()
    ]
    selected = st.selectbox("Choose flight to edit", flight_options)

    # Get the index of the selected flight
    if selected:
        idx = int(selected.split(":")[0])
        row = df.loc[idx]

        # Editable fields
        airline = st.text_input("Airline", value=row.get("Airline", ""))
        aircraft = st.text_input("Aircraft", value=row.get("Aircraft", ""))
        registration = st.text_input("Registration", value=row.get("Regestration", ""))
        seat = st.text_input("Seat", value=row.get("Seat", ""))
        flight_number = st.text_input("Flight Number", value=row.get("Flight Number", ""))
        origin_airport = st.text_input("Origin Airport", value=row.get("origin", ""))
        destination_airport = st.text_input("Destination Airport", value=row.get("destination", ""))
        date = st.text_input("Date", value=row.get("Date", ""))
        origin_address = st.text_input("Origin Address", value=row.get("Origin Address", ""))
        destination_address = st.text_input("Destination Address", value=row.get("Destination Address", ""))

        if st.button("Save Changes"):
            df.at[idx, "Airline"] = airline
            df.at[idx, "Aircraft"] = aircraft
            df.at[idx, "Regestration"] = registration
            df.at[idx, "Seat"] = seat
            df.at[idx, "Flight Number"] = flight_number
            df.at[idx, "origin"] = origin_airport
            df.at[idx, "destination"] = destination_airport
            df.at[idx, "Date"] = date
            df.at[idx, "Origin Address"] = origin_address
            df.at[idx, "Destination Address"] = destination_address
            df.to_csv("data/personal_flight_data.csv", index=False)
            st.success("This ones all set! ✈️")

        # Add this block for deleting the selected flight
        if st.button("Delete Flight", type="primary"):
            df = df.drop(idx).reset_index(drop=True)
            df.to_csv("data/personal_flight_data.csv", index=False)
            st.session_state["delete_success"] = "Flight deleted! Lets keep adding from now on ;)"
            st.experimental_rerun()

        if st.session_state.get("delete_success"):
            st.success(st.session_state["delete_success"])
            del st.session_state["delete_success"]

if selection == "Information":
    st.title("💡 Just to let you know...")

    # Toggle for streak calculation mode (move this to the top)
    if "monthly_streak" not in st.session_state:
        st.session_state["monthly_streak"] = False

    with st.container():
        st.markdown(
            """
            <div style="background-color:#4c4c4c;padding:18px 16px;border-radius:10px;margin-bottom:16px;border:1px solid #e0e0e0;">
                <span style="font-size:1.1em;color:#FFFFFF;">
                    <b>Traveler, frequent traveler, or flying maniac?</b><br>
                    Per default, the streak will be yearly. For all you frequent flyers, you can switch to a monthly streak calculation to up the thrill.
                </span>
            """,
            unsafe_allow_html=True
        )
        btn_label = "Monthly Streak" if not st.session_state["monthly_streak"] else "Yearly Streak"
        btn_clicked = st.button(btn_label, key="toggle_streak_info", help="Toggle streak calculation mode")
        st.markdown("</div>", unsafe_allow_html=True)
        if btn_clicked:
            st.session_state["monthly_streak"] = not st.session_state["monthly_streak"]
            st.experimental_rerun()

    info_boxes = [
        "The color added to each flight is supposed to represent that airlines color. However, some airlines are automatically generated and therefore might not align with what youd expect. Make changes youself through the airline_colors.csv located in the data folder or, if your not tach-savvy, let me know.",
        "Tip: Use the 'Add Data' tab to enter new flights. You can edit or delete any flight in the 'Edit Data' tab later.",
        "The leaf symbol (🍃) next to an aircraft indicates that it is considered a 'green' aircraft, meaning it has lower emissions or is more environmentally friendly compared to other frequently used aircraft.",
        "Your data is saved locally as a CSV file. We dont make backups so if you care about your logbook please do that yourself!",
    ]

    for info in info_boxes:
        st.markdown(
            f"""
            <div style="background-color:#4c4c4c;padding:18px 16px;border-radius:10px;margin-bottom:16px;border:1px solid #e0e0e0;">
                <span style="font-size:1.1em;color:#FFFFFF;">{info}</span>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown(
            f"""
            <div style="text-align:center; margin-bottom: 30px;">
                <span style="font-size: 1em; color: #cdcdcd; ">Made with love in Hamburg EDDH/HAM 🖤</span><br>
                <span style="font-size: 1em; color: #cdcdcd;">by Cole</span>
            </div>
            """,
            unsafe_allow_html=True
        )




