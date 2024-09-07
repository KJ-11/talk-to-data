import streamlit as st
import sqlite3
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_community.llms.OpenAI import OpenAI
import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Get the API key
openai_api_key = os.getenv("OPENAI_API_KEY")


# Chat functionality using LangChain
def chat_interface():
    st.text_input("Ask something...", key="user_input", on_change=handle_user_input)

# Handle user input in the chat
def handle_user_input():
    user_input = st.session_state.user_input
    if user_input:
        response = run_langchain(user_input)
        st.write(response)

# Function to generate SQL queries from natural language
def run_langchain(user_input):
    # Define LangChain's prompt template
    template = """
    Convert the following natural language query into a SQL query:

    {question}

    SQL Query:
    """
    prompt = PromptTemplate(
        input_variables=["question"],
        template=template,
    )
    
    # Use OpenAI for large language model
    llm = OpenAI(openai_api_key=os.getenv("OPENAI_API_KEY"))  
    chain = LLMChain(llm=llm, prompt=prompt)

    # Generate SQL query from natural language
    sql_query = chain.run(user_input)

    # Execute SQL query in the SQLite database
    conn = sqlite3.connect('streamlit_app/db/temp.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute(sql_query)
        result = cursor.fetchall()
        conn.close()
        return result
    except Exception as e:
        return f"Error in query: {str(e)}"
