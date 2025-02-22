import streamlit as st
import pandas as pd
import time, numpy as np
from datetime import datetime

# Set up the page configuration
st.set_page_config(layout="wide")

# Initialize empty DataFrames
df1 = pd.DataFrame(columns=['Column1', 'Column2'])
df2 = pd.DataFrame(columns=['ColumnA', 'ColumnB'])

# Add search bar at the top
search_term = st.text_input("Search DataFrames", "")

# Create three columns
col1, col2, col3 = st.columns([2, 2, 1])

# Create placeholders for the DataFrames and update time
with col1:
    df1_placeholder = st.empty()
    st.write("DataFrame 1")

with col2:
    df2_placeholder = st.empty()
    st.write("DataFrame 2")

with col3:
    st.write("Last Update")
    update_time_placeholder = st.empty()

# Function to filter DataFrame based on search term
def filter_dataframe(df, term):
    if term:
        # Convert all values to string and search
        mask = df.astype(str).apply(lambda x: x.str.contains(term, case=False, na=False)).any(axis=1)
        return df[mask]
    return df

# Loop to update DataFrames
def update_dataframes():
    global df1, df2
    for i in range(100):
        # YOUR PLACEHOLDER CODE HERE
        myname = np.random.choice(['Brandon','Josh','Jon'])
        new_data1 = pd.DataFrame({
            'Column1': [myname, myname],
            'Column2': [i, i+1],
            'Column3': [i*2, i*3]
        })
        
        new_data2 = pd.DataFrame({
            'Column1': [myname, myname],
            'Column2': [i, i+1],
            'Column3': [i*2, i*3]
        })
        
        # Update the DataFrames
        df1 = new_data1
        df2 = new_data2
        
        # Get current time
        current_time = datetime.now().strftime("%H:%M:%S")
        
        # Filter DataFrames based on search term
        filtered_df1 = filter_dataframe(df1, search_term)
        filtered_df2 = filter_dataframe(df2, search_term)
        
        # Display filtered DataFrames without index
        with col1:
            df1_placeholder.dataframe(filtered_df1, hide_index=True)
        
        with col2:
            df2_placeholder.dataframe(filtered_df2, hide_index=True)
        
        # Update the time display
        with col3:
            update_time_placeholder.text(f"Last updated: {current_time}")
        
        time.sleep(5)

# Run the update function
if st.button("Start Updates"):
    update_dataframes()

# Initial display with filtering
filtered_df1 = filter_dataframe(df1, search_term)
filtered_df2 = filter_dataframe(df2, search_term)
df1_placeholder.dataframe(filtered_df1, hide_index=True)
df2_placeholder.dataframe(filtered_df2, hide_index=True)
update_time_placeholder.text(f"Last updated: {datetime.now().strftime('%H:%M:%S')}")