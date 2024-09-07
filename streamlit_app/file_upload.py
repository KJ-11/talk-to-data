import os
import sqlite3
import pandas as pd
import streamlit as st

# Function to handle file upload and return the DataFrame for preview
def upload_file():
    uploaded_file = st.file_uploader("Upload a CSV, XLSX, or TXT file", type=["csv", "xlsx", "txt", "tsv"])

    if uploaded_file is not None:
        st.session_state['uploaded_file'] = uploaded_file  # Store the file in session state

        try:
            # Process the file based on the file type
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            elif uploaded_file.name.endswith('.xlsx'):
                df = pd.read_excel(uploaded_file)
            elif uploaded_file.name.endswith('.txt') or uploaded_file.name.endswith('.tsv'):
                df = pd.read_csv(uploaded_file, delimiter='\t')

            # Save the DataFrame to SQLite database
            save_to_db(df)

            # Return the DataFrame for preview
            return df

        except Exception as e:
            st.error(f"Error processing file: {str(e)}")

    return None  # Return None if no file is uploaded or an error occurs

# Function to save the data to SQLite and ensure the database directory exists
def save_to_db(df):
    # Ensure the db directory exists
    db_dir = os.path.join(os.path.dirname(__file__), 'db')
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)  # Create the db directory if it doesn't exist

    # Define the path for the SQLite database
    db_path = os.path.join(db_dir, 'temp.db')

    # Connect to SQLite and save the data
    try:
        conn = sqlite3.connect(db_path)
        df.to_sql('uploaded_data', conn, if_exists='replace', index=False)
        conn.close()
        st.success(f"Data saved to database at: {db_path}")
    except sqlite3.Error as e:
        st.error(f"Error saving to database: {str(e)}")
