import re
import streamlit as st
import openai
import sqlite3
import os
from dotenv import load_dotenv
from file_upload import upload_file
import pandas as pd

# Load environment variables from the .env file
load_dotenv()

# Get the OpenAI API key from the environment variable
openai_api_key = os.getenv("OPENAI_API_KEY")

# ChatGPT (via GPT-4) to generate SQL queries or respond to broader questions
def chat_interface(df):
    user_input = st.text_input("Ask something about the data...", key="user_input")
    
    if user_input:
        # Step 1: Use GPT-4 to decide if it's a broad question or SQL query
        response, is_sql = generate_response_or_query(user_input, df)
        st.write(f"Response: {response}")
        
        # If it's a valid SQL query, execute it
        if is_sql:
            sql_query = extract_sql_query(response)  # Extract SQL part only
            result = execute_sql_query(sql_query)
            st.write(result)
        else:
            st.write(response)

# Step 1: Generate a response, deciding if it's a SQL query or broad question
def generate_response_or_query(user_input, df):
    openai.api_key = openai_api_key
    
    # Get column names from the DataFrame
    column_names = ', '.join([f'"{col}"' for col in df.columns.tolist()])  # Ensure column names are quoted
    
    # Attempt to detect date formats (if applicable)
    date_format = detect_date_format(df)
    if date_format:
        date_format_prompt = f"The date format used in this dataset is '{date_format}'. Make sure all dates are in this format."
    else:
        date_format_prompt = ""

    # Craft a prompt for GPT-4 to either generate a valid SQL query or respond to a broad question
    prompt = f"""
    You are an AI that helps with data analysis. You can either answer questions directly or generate SQL queries depending on the user's query.
    The table name is 'uploaded_data'. The available columns are: {column_names}.
    {date_format_prompt}
    
    If the user's question can be answered without a SQL query, provide a direct answer. If a SQL query is needed, generate a valid SQL query using the exact column names provided, without modifying them.

    Query: "{user_input}"

    Response:
    """
    
    try:
        # Using the updated OpenAI API for chat completions (v1.0.0 and higher)
        response = openai.chat.completions.create(
            model="gpt-4",  # Specify the GPT-4 model
            messages=[
                {"role": "system", "content": "You are an assistant that helps generate SQL queries and answer data-related questions."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=250,
            temperature=0.5,
        )
        
        # Correct access to the response content
        response_text = response.choices[0].message.content.strip()
        
        # Check if the response is an SQL query (basic heuristic, you can improve this logic)
        if response_text.strip().lower().startswith("select") or "from" in response_text.lower():
            return response_text, True  # It's a SQL query
        else:
            return response_text, False  # It's a broad question or direct answer
    
    except Exception as e:
        return f"Error: {str(e)}", False

# Extract only the SQL part of the response, ignoring non-SQL text
def extract_sql_query(response_text):
    # Use a regex to extract the SQL query portion, starting with SELECT or other SQL keywords
    sql_match = re.search(r'(SELECT .*?;)', response_text, re.IGNORECASE | re.DOTALL)
    if sql_match:
        return sql_match.group(1)
    else:
        return None  # No valid SQL found

# Step 2: Execute the SQL query in SQLite database
def execute_sql_query(sql_query):
    db_path = os.path.join(os.path.dirname(__file__), 'db/temp.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        cursor.execute(sql_query)
        result = cursor.fetchall()
        conn.close()
        return result
    except Exception as e:
        return f"Error executing SQL query: {str(e)}"

# Function to detect the date format in the dataset
def detect_date_format(df):
    # Look for a date column in the dataset
    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            # Infer the date format based on the first valid date in the column
            sample_date = df[col].dropna().iloc[0]
            return sample_date.strftime('%Y-%m-%d')  # Modify this to match your date format
    return None  # Return None if no date columns are found

# Main App Layout
def main():
    st.set_page_config(layout="wide")

    # Sidebar for file upload
    with st.sidebar:
        st.title("Databases")
        df = upload_file()

        if 'uploaded_file' in st.session_state and st.session_state['uploaded_file'] is not None:
            st.write(f"Uploaded file: {st.session_state['uploaded_file'].name}")
        else:
            st.write("No file uploaded yet.")

    # Main layout with two columns: col1 for database preview, col2 for chat
    col1, col2 = st.columns([2, 1])

    # Middle panel: Database preview
    with col1:
        st.title("Database Preview")
        if df is not None:
            st.subheader("Columns")
            st.write(df.columns.tolist())  # Show columns
            st.subheader("Data")
            st.write(df.head(10))  # Show first 10 rows of data
        else:
            st.write("No database uploaded yet.")

    # Right panel: Chat with the database
    with col2:
        st.title("Chat with Database")
        if df is not None:
            chat_interface(df)  # Pass DataFrame to chat interface to use the column structure

if __name__ == "__main__":
    main()
